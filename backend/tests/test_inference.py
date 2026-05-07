from app.ml.inference import EmotionClassifier


def test_negated_positive_is_negative():
    classifier = EmotionClassifier(model_dir="missing-model-dir")
    prediction = classifier.predict("I am not feeling good today")
    assert prediction.emotion in {"sad", "disappointed"}


def test_not_happy_is_not_joyful():
    classifier = EmotionClassifier(model_dir="missing-model-dir")
    prediction = classifier.predict("I am not happy today")
    assert prediction.emotion != "happy"
