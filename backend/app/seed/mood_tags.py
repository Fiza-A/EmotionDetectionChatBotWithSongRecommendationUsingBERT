NEGATIVE_BLOCK_TAGS = {"sad", "melancholic", "heartbreak", "grief", "tragedy", "dark", "horror", "depressing"}

MOVIE_MOOD_RULES = [
    ({"comedy", "family", "animation", "adventure", "feel-good"}, {"happy", "uplifting", "feel-good"}),
    ({"romance", "drama"}, {"calm", "comforting", "hopeful"}),
    ({"action", "sport", "sports", "adventure"}, {"energetic", "excited"}),
    ({"documentary", "biography", "biopic"}, {"inspiring", "hopeful"}),
    ({"thriller", "horror", "tragedy", "dark"}, {"dark"}),
]

SONG_MOOD_RULES = [
    ({"happy", "upbeat", "dance", "pop", "party"}, {"happy", "upbeat", "energetic"}),
    ({"calm", "acoustic", "chill", "lo-fi", "lofi", "ambient"}, {"calm", "comforting"}),
    ({"devotional", "sufi", "spiritual", "bhajan"}, {"calm", "comforting", "hopeful"}),
    ({"comedy", "fun"}, {"uplifting", "feel-good"}),
    ({"sad", "heartbreak", "grief"}, {"sad", "melancholic"}),
]

POSITIVE_WORDS = {"hope", "dream", "smile", "friend", "love", "happy", "shine", "journey", "light", "win"}


def normalize_tags(tags: str | list[str] | None) -> list[str]:
    if not tags:
        return []
    if isinstance(tags, str):
        parts = tags.replace("|", ",").replace(";", ",").split(",")
    else:
        parts = tags
    normalized = []
    for tag in parts:
        value = str(tag).strip().lower()
        if value and value not in normalized:
            normalized.append(value)
    return normalized


def generate_mood_tags(kind: str, genre: str | None = None, raw_tags: str | None = None, title: str | None = None, overview: str | None = None) -> list[str]:
    words = set(normalize_tags(genre)) | set(normalize_tags(raw_tags))
    text = f"{title or ''} {overview or ''}".lower()
    if any(word in text for word in POSITIVE_WORDS):
        words.add("hopeful")
    rules = SONG_MOOD_RULES if kind == "song" else MOVIE_MOOD_RULES
    mood_tags: set[str] = set()
    for triggers, outputs in rules:
        if words.intersection(triggers) or any(trigger in text for trigger in triggers):
            mood_tags.update(outputs)
    if not mood_tags:
        mood_tags.update({"feel-good", "calm"} if kind == "movie" else {"calm", "comforting"})
    return sorted(mood_tags)


def tags_to_text(tags: str | list[str] | None) -> str:
    return ",".join(normalize_tags(tags))
