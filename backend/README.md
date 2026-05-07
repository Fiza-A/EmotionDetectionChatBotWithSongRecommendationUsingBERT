# Emotion Detection Chatbot Backend

FastAPI backend with SQLite persistence, JWT authentication, recommendation personalization, GoEmotions ELECTRA training scripts, and fallback inference.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed.seed_recommendations
uvicorn app.main:app --reload
```

The API will run at `http://localhost:8000`.

## Train ELECTRA on GoEmotions

You can use Hugging Face's `go_emotions` loader directly:

```bash
python -m app.ml.train --model-name google/electra-base-discriminator --epochs 3 --batch-size 16
```

For Kaggle, download the GoEmotions dataset from Kaggle, place the CSV locally, then pass it:

```bash
python -m app.ml.train --dataset-path path\to\goemotions.csv --output-dir model_artifacts\electra-goemotions
```

The trainer uses max length `128`, learning rate `2e-5`, macro F1 as the best-model metric, and reports accuracy, F1, precision, and recall. The backend loads saved artifacts from `MODEL_DIR` (`model_artifacts/electra-goemotions` by default). If the model is absent, it uses a documented rule-based fallback with a negation guard.

## iTunes Song Preview Enrichment

Songs can be enriched with free iTunes Search API metadata: 30-second preview URL, album art, and Apple Music link.

```bash
python -m app.seed.seed_recommendations --itunes
python scripts/check_itunes_songs.py
```

The checker writes `itunes_song_check.json` in the backend folder and reports which seeded songs were found with previews.

## Evaluate

```bash
python -m app.ml.evaluate --model-dir model_artifacts\electra-goemotions
```

## API

- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`
- `PUT /users/preferences`
- `POST /chat/message`
- `GET /chat/history`
- `GET /mood/history`
- `GET /recommendations?emotion=sad`
- `POST /recommendations/feedback`
