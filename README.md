# Emotion Detection Chatbot

MoodMate is a full-stack emotion-aware chatbot. It detects a primary emotion from user text, stores mood history, and recommends songs and movies in preferred languages. Negative moods are mapped to uplifting, calming, hopeful, funny, or comforting content instead of sadder recommendations.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite by default, JWT auth, bcrypt password hashing
- ML: PyTorch + Hugging Face Transformers, default `google/electra-base-discriminator`, GoEmotions label mapping
- Frontend: React + Vite, Tailwind CSS, Framer Motion, Recharts, Axios
- Data: multilingual recommendation seed data for English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi, Punjabi, and Gujarati

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed.seed_recommendations
uvicorn app.main:app --reload
```

## Run Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Train The Model

The app runs before training through a fallback inference mode. For the transformer model:

```bash
cd backend
python -m app.ml.train --model-name google/electra-base-discriminator --epochs 3 --batch-size 16
```

To train from a Kaggle CSV download:

```bash
python -m app.ml.train --dataset-path path\to\goemotions.csv
```

Saved artifacts go to `backend/model_artifacts/electra-goemotions` from the repository view (`model_artifacts/electra-goemotions` while inside `backend`) and are loaded automatically by the API.

## iTunes Previews

The backend can enrich song recommendations with free iTunes Search API results, including 30-second `previewUrl`, `artworkUrl100`, and Apple Music links:

```bash
cd backend
python -m app.seed.seed_recommendations --itunes
python scripts/check_itunes_songs.py
```

## Notes

The chatbot is not a therapist or medical diagnostic tool. It includes a basic self-harm keyword safety response and encourages immediate trusted or emergency support when triggered.
