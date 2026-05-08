# Emotion Detection Chatbot With Song And Movie Recommendations

## Abstract

MoodMate is a full-stack emotion detection chatbot that reads a user's text message, predicts the user's primary mood, stores the conversation and mood history, and recommends songs and movies that match or improve that mood. The system is built around an ELECTRA/BERT-style transformer emotion classifier trained for the GoEmotions label space, with a fallback rule-based inference mode so the application can still run before a model is trained locally.

The project combines machine learning, backend APIs, database persistence, recommendation filtering, iTunes audio previews, and a responsive React chatbot interface. Users can register, log in, select preferred recommendation languages, start new conversations, revisit old chats, and receive mood-aware recommendations. For happy or excited moods, the bot recommends upbeat and positive content. For sad, angry, anxious, lonely, disappointed, or otherwise negative moods, the bot avoids sad or depressing content and instead recommends uplifting, calming, comforting, hopeful, devotional, comedy, or feel-good songs and movies.

The chatbot is not a therapist and does not diagnose mental health conditions. It includes only a basic self-harm keyword safety response that encourages the user to contact trusted people or local emergency services when needed.

## Main Features

- Emotion prediction from user text using an ELECTRA/BERT-compatible transformer pipeline.
- GoEmotions-style fine-grained label mapping into simple chatbot moods.
- Negation-aware fallback handling for sentences such as "I am not happy" or "I don't feel okay".
- JWT authentication with bcrypt password hashing.
- Conversation history similar to ChatGPT, with New Chat and Recents support.
- Per-user mood history and recommendation feedback.
- Strict language-based recommendation filtering.
- Song and movie recommendation bundles with up to 3 songs and 3 movies.
- iTunes Search API enrichment for 30-second song preview clips, album art, and Apple Music links.
- Multilingual recommendation catalog for English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi, Punjabi, and Gujarati.
- Modern React chatbot UI with fixed sidebar, fixed header, fixed input bar, and scrollable messages panel.

## Technology Stack

### Machine Learning

- Python
- PyTorch
- Hugging Face Transformers
- Hugging Face Datasets
- ELECTRA default model: `google/electra-base-discriminator`
- GoEmotions dataset label mapping
- Accuracy, precision, recall, and F1-score evaluation

### Backend

- FastAPI
- SQLAlchemy ORM
- SQLite for local development
- PostgreSQL-compatible configuration through `DATABASE_URL`
- JWT authentication
- bcrypt password hashing
- Pydantic request/response validation
- iTunes Search API integration

### Frontend

- React with Vite
- Tailwind CSS
- Framer Motion
- Axios
- Recharts
- Lucide React icons

## How Emotion Prediction Works

The prediction layer is located in `backend/app/ml/`.

Training code:

- `backend/app/ml/train.py`
- `backend/app/ml/evaluate.py`
- `backend/app/ml/inference.py`
- `backend/app/ml/label_mapping.py`

The training script fine-tunes an ELECTRA/BERT-compatible transformer on GoEmotions data. GoEmotions contains fine-grained labels such as joy, sadness, anger, fear, disappointment, grief, optimism, love, confusion, approval, and neutral. The chatbot maps these detailed emotions into simpler user-facing moods:

- `happy`
- `sad`
- `angry`
- `anxious`
- `disappointed`
- `lonely`
- `excited`
- `calm`
- `neutral`

Example mapping:

- `joy`, `amusement`, `gratitude`, `love`, `optimism` -> happy or excited
- `sadness`, `grief`, `remorse` -> sad
- `disappointment` -> disappointed
- `anger`, `annoyance`, `disapproval` -> angry
- `fear`, `nervousness`, `confusion` -> anxious
- `approval`, `admiration`, `caring`, `relief` -> calm or positive
- `neutral` -> neutral

The backend first tries to load trained model artifacts from `MODEL_DIR`, which defaults to:

```text
backend/model_artifacts/electra-goemotions
```

If model files are missing, the app uses a documented fallback classifier. This fallback uses mood keywords plus negation-aware rules so obvious phrases are handled more safely. For example:

- "I am not happy today" should not become `happy`.
- "I am not feeling good" should become a negative mood.
- "I don't feel okay" should be treated as negative.

The API returns a clear primary emotion and confidence score for each chat message.

## GoEmotions Training

You can train using the Hugging Face GoEmotions dataset loader:

```bash
cd backend
python -m app.ml.train --model-name google/electra-base-discriminator --epochs 3 --batch-size 16
```

Or train from a Kaggle GoEmotions CSV:

```bash
cd backend
python -m app.ml.train --dataset-path path\to\goemotions.csv --output-dir model_artifacts\electra-goemotions
```

Default training settings:

- Model: `google/electra-base-discriminator`
- Tokenizer: matching Hugging Face tokenizer
- Max sequence length: `128`
- Batch size: configurable, commonly `16`
- Learning rate: `2e-5`
- Epochs: configurable, commonly `3`
- Metrics: accuracy, precision, recall, macro F1

After training, saved artifacts are loaded automatically by the backend inference service.

## Recommendation System

The recommendation system is database-backed and lives mainly in:

- `backend/app/services/recommendation_service.py`
- `backend/app/seed/catalog.py`
- `backend/app/seed/expanded_catalog.py`
- `backend/app/seed/seed_recommendations.py`
- `backend/app/seed/import_movies.py`
- `backend/app/seed/import_songs.py`
- `backend/app/seed/import_from_csv.py`
- `backend/app/seed/enrich_music_tags.py`
- `backend/app/seed/enrich_movie_tags.py`

Each recommendation record stores:

- title
- type: `song` or `movie`
- language
- mood tags
- genre
- creator, artist, or director
- release year
- link
- image URL or poster URL
- iTunes preview URL for songs when available
- album art for songs when available
- source and source ID
- popularity score

Recommendation logic uses two controls:

1. Mood controls the emotional category.
2. User language preferences strictly control allowed languages.

A recommendation is valid only if its language is selected by the logged-in user. The backend never falls back to English, Hindi, or any other language unless that language is selected in preferences.

For negative moods such as sad, angry, anxious, lonely, and disappointed, the backend uses uplifting tags such as:

- uplifting
- comforting
- calming
- hopeful
- devotional
- comedy
- feel-good

It avoids recommending content tagged as:

- sad
- heartbreak
- grief
- depressing
- melancholic
- tragedy
- dark
- horror

The chat response returns recommendations in this shape:

```json
{
  "recommendations": {
    "songs": [],
    "movies": [],
    "message": null
  }
}
```

## iTunes 30-Second Song Clips

The project uses Apple's free iTunes Search API for song previews. The API returns `previewUrl` for track results, which points to a 30-second audio preview file.

Documentation:

```text
https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/UnderstandingSearchResults.html
```

The integration is implemented in:

- `backend/app/services/itunes_service.py`
- `backend/app/services/recommendation_service.py`
- `backend/scripts/check_itunes_songs.py`

When a song recommendation is selected and does not already have a preview URL, the backend searches iTunes using the song title and artist. If a preview is found, it stores:

- `preview_url`
- `album_art`
- `external_url`

The frontend recommendation card already contains an audio player. If `preview_url` exists, the song card shows a playable 30-second audio control.

To enrich seeded songs manually:

```bash
cd backend
python -m app.seed.seed_recommendations --itunes
```

To test iTunes availability:

```bash
cd backend
python scripts/check_itunes_songs.py
```

## Frontend UI

The frontend is located in `frontend/src/`.

Important folders:

- `frontend/src/pages/`
- `frontend/src/components/`
- `frontend/src/services/`
- `frontend/src/hooks/`
- `frontend/src/styles/`

The UI is a modern chatbot interface inspired by ChatGPT-style layout behavior:

- Full viewport app height.
- Fixed left sidebar.
- Fixed top chat header.
- Fixed bottom message input.
- Only the chat messages panel scrolls.
- Conversation recommendations appear inside the scrollable messages area.
- Responsive behavior for smaller screens.

Core screens:

- Login page
- Register page
- Chat page
- Preferences page
- Mood history dashboard

The chat screen displays:

- user messages
- bot responses
- detected emotion and confidence
- song recommendation cards
- movie recommendation cards
- iTunes audio previews when available
- like/dislike feedback buttons

The frontend does not hardcode recommendation fallbacks. It renders whatever the backend returns.

## Backend Workflow

When a user sends a chat message:

1. The frontend sends `POST /chat/message` with the message text and optional conversation ID.
2. The backend authenticates the JWT token.
3. The backend creates a conversation if needed.
4. The user message is saved in `chat_messages`.
5. The inference service predicts emotion and confidence.
6. Mood history is saved in `mood_history`.
7. The recommendation service reads the user's selected languages.
8. Songs and movies are queried separately from the database.
9. Negative moods are mapped to uplifting or calming recommendation tags.
10. Recently shown recommendations are avoided when alternatives exist.
11. Song recommendations are enriched with iTunes previews when possible.
12. Bot response and recommendation JSON are saved.
13. The API returns the conversation ID, user message, bot message, detected emotion, confidence score, and recommendations.

## Database Tables

The local development database uses SQLite by default.

Main tables:

- `users`
- `user_preferences`
- `conversations`
- `chat_messages`
- `mood_history`
- `recommendations`
- `recommendation_events`

Conversation history is user-specific. A user can only access their own conversations.

## API Endpoints

Authentication:

- `POST /auth/register`
- `POST /auth/login`

Users:

- `GET /users/me`
- `PUT /users/preferences`

Conversations:

- `POST /conversations`
- `GET /conversations`
- `GET /conversations/{conversation_id}`
- `PATCH /conversations/{conversation_id}`
- `DELETE /conversations/{conversation_id}`

Chat and mood:

- `POST /chat/message`
- `GET /chat/history`
- `GET /mood/history`

Recommendations:

- `GET /recommendations?emotion=sad`
- `POST /recommendations/feedback`

## Project Structure

```text
emotion-chatbot/
  backend/
    app/
      main.py
      config.py
      database.py
      auth/
      ml/
      models/
      routes/
      schemas/
      seed/
      services/
    data/
    scripts/
    tests/
    requirements.txt
    .env.example
    README.md
  frontend/
    src/
      components/
      pages/
      services/
      hooks/
      styles/
    package.json
    README.md
  README.md
```

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed.seed_recommendations
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Recommendation Import Commands

Optional local data files can be placed in `backend/data/`:

- `movies.csv`
- `songs.csv`
- `imdb_title_basics.tsv`
- `imdb_title_ratings.tsv`
- `tmdb_movies.csv`
- `indian_regional_movies.csv`

The app does not fail if these files are missing. Import scripts print a clear message instead.

Commands:

```bash
cd backend
python -m app.seed.import_movies --source csv --file backend/data/movies.csv
python -m app.seed.import_songs --source csv --file backend/data/songs.csv
python -m app.seed.import_movies --source imdb
python -m app.seed.import_movies --source tmdb --language Hindi --limit 500
python -m app.seed.import_songs --source musicbrainz --language Hindi --limit 500
python -m app.seed.enrich_music_tags
python -m app.seed.enrich_movie_tags
```

API-backed imports run only if keys are configured:

```text
TMDB_API_KEY=
LASTFM_API_KEY=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

## Environment Variables

Backend variables are defined in `backend/.env.example`.

Important values:

- `DATABASE_URL`
- `SECRET_KEY`
- `ENVIRONMENT`
- `MODEL_DIR`
- `FALLBACK_INFERENCE`
- `TMDB_API_KEY`
- `LASTFM_API_KEY`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

Security note: the backend rejects the default `SECRET_KEY=change-me-in-production` outside development and test environments.

Frontend variables are defined in `frontend/.env.example`.

Important value:

- `VITE_API_URL`

## Testing

Backend:

```bash
cd backend
pytest tests
```

Frontend build:

```bash
cd frontend
npm run build
```

iTunes checker:

```bash
cd backend
python scripts/check_itunes_songs.py
```

## Safety And Limitations

MoodMate is an educational emotion-aware recommendation chatbot. It does not provide medical advice, therapy, diagnosis, or crisis counseling. The emotion classifier can make mistakes, especially with sarcasm, mixed emotions, short messages, and domain-specific language.

If self-harm intent is detected, the chatbot shows a supportive safety message and encourages the user to contact trusted people or local emergency services.
