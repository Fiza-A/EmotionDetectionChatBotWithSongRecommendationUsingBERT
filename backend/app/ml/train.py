import argparse
from pathlib import Path

import numpy as np
from datasets import DatasetDict, load_dataset, load_from_disk
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from app.ml.label_mapping import GOEMOTIONS_LABELS


def load_goemotions(dataset_path: str | None) -> DatasetDict:
    if dataset_path:
        path = Path(dataset_path)
        if path.is_dir() and (path / "dataset_info.json").exists():
            return load_from_disk(str(path))
        return load_dataset("csv", data_files={"train": str(path)})
    return load_dataset("go_emotions", "simplified")


def normalize_labels(example):
    labels = example.get("labels")
    if labels is None and "label" in example:
        labels = [int(example["label"])]
    if isinstance(labels, str):
        labels = [int(x) for x in labels.replace("[", "").replace("]", "").split(",") if x.strip()]
    primary = labels[0] if labels else GOEMOTIONS_LABELS.index("neutral")
    example["label"] = int(primary)
    return example


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_macro": f1_score(labels, preds, average="macro", zero_division=0),
        "precision_macro": precision_score(labels, preds, average="macro", zero_division=0),
        "recall_macro": recall_score(labels, preds, average="macro", zero_division=0),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", default=None, help="Optional Kaggle CSV or HF dataset saved path.")
    parser.add_argument("--model-name", default="google/electra-base-discriminator")
    parser.add_argument("--output-dir", default="model_artifacts/electra-goemotions")
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--epochs", type=float, default=3)
    args = parser.parse_args()

    dataset = load_goemotions(args.dataset_path).map(normalize_labels)
    if "validation" not in dataset:
        split = dataset["train"].train_test_split(test_size=0.15, seed=42)
        dataset = DatasetDict(train=split["train"], validation=split["test"])

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    encoded = dataset.map(tokenize, batched=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(GOEMOTIONS_LABELS),
        id2label={i: label for i, label in enumerate(GOEMOTIONS_LABELS)},
        label2id={label: i for i, label in enumerate(GOEMOTIONS_LABELS)},
    )
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encoded["train"],
        eval_dataset=encoded["validation"],
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.evaluate()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
