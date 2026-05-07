from app.ml.inference import EmotionClassifier
from app.ml.label_mapping import GOEMOTIONS_LABELS


def test_negated_positive_is_negative():
    classifier = EmotionClassifier(model_dir="missing-model-dir")
    prediction = classifier.predict("I am not feeling good today")
    assert prediction.emotion in {"sad", "disappointed"}


def test_not_happy_is_not_joyful():
    classifier = EmotionClassifier(model_dir="missing-model-dir")
    prediction = classifier.predict("I am not happy today")
    assert prediction.emotion != "happy"


class FakeEncoded(dict):
    def to(self, device):
        return self


class FakeTokenizer:
    def __call__(self, text, truncation, padding, max_length, return_tensors):
        return FakeEncoded(input_ids=[1, 2, 3])


class FakeTensor(list):
    def detach(self):
        return self

    def cpu(self):
        return self


class FakeNoGrad:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeTorch:
    @staticmethod
    def no_grad():
        return FakeNoGrad()

    @staticmethod
    def softmax(logits, dim=-1):
        return FakeTensor(logits)

    @staticmethod
    def argmax(values):
        return max(range(len(values)), key=lambda index: values[index])


class FakeOutput:
    def __init__(self, logits):
        self.logits = [logits]


class FakeModel:
    class Config:
        id2label = {}

    config = Config()

    def __call__(self, **encoded):
        logits = [0.01] * len(GOEMOTIONS_LABELS)
        logits[GOEMOTIONS_LABELS.index("joy")] = 0.9
        return FakeOutput(logits)


def test_transformer_prediction_uses_instance_torch_without_name_error():
    classifier = EmotionClassifier(model_dir="missing-model-dir")
    classifier.tokenizer = FakeTokenizer()
    classifier.model = FakeModel()
    classifier.torch = FakeTorch()

    prediction = classifier.predict("I feel joy today")

    assert prediction.raw_label == "joy"
    assert prediction.emotion == "happy"
