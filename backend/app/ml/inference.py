import re
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings
from app.ml.label_mapping import GOEMOTIONS_LABELS, MOOD_LABELS, map_goemotion_to_mood


NEGATION_RE = re.compile(r"\b(not|never|no|don't|dont|doesn't|doesnt|didn't|didnt|can't|cant|won't|wont)\b", re.I)
POSITIVE_RE = re.compile(r"\b(good|great|happy|okay|ok|fine|joy|excited|love|awesome|wonderful)\b", re.I)


@dataclass
class EmotionPrediction:
    emotion: str
    confidence: float
    raw_label: str
    scores: dict[str, float]
    used_fallback: bool = False


class EmotionClassifier:
    def __init__(self, model_dir: str | Path | None = None):
        self.settings = get_settings()
        self.model_dir = Path(model_dir or self.settings.resolved_model_dir)
        self.tokenizer = None
        self.model = None
        self.torch = None
        self.device = "cpu"
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_dir.exists():
            return
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self.torch = torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
            self.model.to(self.device)
            self.model.eval()
        except Exception:
            self.tokenizer = None
            self.model = None

    def predict(self, text: str) -> EmotionPrediction:
        if self.model and self.tokenizer:
            prediction = self._predict_transformer(text)
        else:
            prediction = self._predict_rules(text)
        return self._apply_negation_guard(text, prediction)

    def _predict_transformer(self, text: str) -> EmotionPrediction:
        encoded = self.tokenizer(text, truncation=True, padding=True, max_length=128, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            logits = self.model(**encoded).logits[0]
            probabilities = torch.softmax(logits, dim=-1).detach().cpu()
        idx = int(torch.argmax(probabilities))
        raw_label = GOEMOTIONS_LABELS[idx] if idx < len(GOEMOTIONS_LABELS) else self.model.config.id2label.get(idx, "neutral")
        mood = map_goemotion_to_mood(raw_label)
        scores = {GOEMOTIONS_LABELS[i]: float(probabilities[i]) for i in range(min(len(GOEMOTIONS_LABELS), len(probabilities)))}
        return EmotionPrediction(mood, float(probabilities[idx]), raw_label, scores)

    def _predict_rules(self, text: str) -> EmotionPrediction:
        normalized = text.lower()
        rules = [
            ("lonely", 0.82, ["lonely", "alone", "isolated", "left out"]),
            ("sad", 0.80, ["sad", "low", "down", "cry", "heartbroken", "depressed", "miserable"]),
            ("disappointed", 0.78, ["disappointed", "let down", "failed", "hopeless", "regret"]),
            ("angry", 0.80, ["angry", "mad", "furious", "irritated", "annoyed", "hate"]),
            ("anxious", 0.79, ["anxious", "worried", "scared", "afraid", "nervous", "panic", "confused"]),
            ("excited", 0.78, ["excited", "thrilled", "pumped", "can't wait", "cant wait"]),
            ("happy", 0.80, ["happy", "great", "good", "awesome", "wonderful", "joy", "love"]),
            ("calm", 0.72, ["calm", "peaceful", "relaxed", "relieved", "okay", "ok", "fine"]),
        ]
        for mood, confidence, keywords in rules:
            if any(keyword in normalized for keyword in keywords):
                return EmotionPrediction(mood, confidence, mood, {mood: confidence}, used_fallback=True)
        return EmotionPrediction("neutral", 0.58, "neutral", {"neutral": 0.58}, used_fallback=True)

    def _apply_negation_guard(self, text: str, prediction: EmotionPrediction) -> EmotionPrediction:
        window = text.lower()
        has_negated_positive = bool(NEGATION_RE.search(window) and POSITIVE_RE.search(window))
        if has_negated_positive and prediction.emotion in {"happy", "excited", "calm", "neutral"}:
            target = "sad" if re.search(r"\b(good|okay|ok|fine)\b", window) else "disappointed"
            scores = dict(prediction.scores)
            scores[target] = max(scores.get(target, 0), 0.84)
            return EmotionPrediction(target, 0.84, target, scores, used_fallback=prediction.used_fallback)
        return prediction


classifier = EmotionClassifier()
