import argparse

import numpy as np
from datasets import load_dataset
from sklearn.metrics import classification_report
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer

from app.ml.label_mapping import GOEMOTIONS_LABELS
from app.ml.train import normalize_labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default="model_artifacts/electra-goemotions")
    parser.add_argument("--split", default="test")
    args = parser.parse_args()

    dataset = load_dataset("go_emotions", "simplified")[args.split].map(normalize_labels)
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_dir)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=128)

    encoded = dataset.map(tokenize, batched=True)
    trainer = Trainer(model=model, tokenizer=tokenizer)
    output = trainer.predict(encoded)
    preds = np.argmax(output.predictions, axis=-1)
    print(classification_report(output.label_ids, preds, target_names=GOEMOTIONS_LABELS, zero_division=0))


if __name__ == "__main__":
    main()
