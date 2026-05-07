from app.seed.catalog import LANGUAGES


SONG_MOODS = [
    ("Sunrise", "happy,upbeat,energetic", "Pop"),
    ("Festival Lights", "happy,upbeat,party", "Dance"),
    ("Hope Road", "uplifting,hopeful,feel-good", "Soundtrack"),
    ("Smile Again", "uplifting,comforting,hopeful", "Pop"),
    ("Quiet River", "calm,comforting", "Acoustic"),
    ("Soft Evening", "calm,comforting,chill", "Lo-fi"),
    ("Victory Beat", "energetic,excited,upbeat", "Pop"),
    ("Friendship Tune", "feel-good,uplifting,happy", "Soundtrack"),
    ("Morning Prayer", "calm,comforting,hopeful", "Devotional"),
    ("Dance Street", "happy,upbeat,energetic", "Dance"),
]

MOVIE_MOODS = [
    ("Laugh Lane", "comedy,feel-good,happy", "Comedy"),
    ("Family Weekend", "family,comforting,feel-good", "Family"),
    ("Hope House", "uplifting,hopeful,comforting", "Drama"),
    ("Bright Journey", "adventure,excited,feel-good", "Adventure"),
    ("Calm Harbor", "calm,comforting,hopeful", "Drama"),
    ("Dream Team", "inspiring,uplifting,feel-good", "Sports"),
    ("Friendly Chaos", "comedy,friendship,feel-good", "Comedy"),
    ("Little Wonders", "animation,family,happy", "Animation"),
    ("New Beginning", "hopeful,comforting,feel-good", "Drama"),
    ("Festival Friends", "happy,comedy,uplifting", "Comedy"),
]

LANGUAGE_CREATORS = {
    "English": ("Various Artists", "Independent Studio"),
    "Hindi": ("Bollywood Ensemble", "Mumbai Pictures"),
    "Tamil": ("Kollywood Collective", "Chennai Films"),
    "Telugu": ("Tollywood Voices", "Hyderabad Studios"),
    "Malayalam": ("Mollywood Ensemble", "Kochi Films"),
    "Kannada": ("Sandalwood Collective", "Bengaluru Studios"),
    "Bengali": ("Bengal Music Circle", "Kolkata Films"),
    "Marathi": ("Marathi Music House", "Pune Pictures"),
    "Punjabi": ("Punjabi Pop Collective", "Punjab Films"),
    "Gujarati": ("Gujarati Folk Circle", "Ahmedabad Studios"),
}


def generated_seed_items() -> list[tuple]:
    items = []
    for language in LANGUAGES:
        song_creator, movie_creator = LANGUAGE_CREATORS[language]
        for index in range(50):
            title, tags, genre = SONG_MOODS[index % len(SONG_MOODS)]
            items.append(
                (
                    f"{language} {title} {index + 1}",
                    "song",
                    language,
                    tags,
                    genre,
                    song_creator,
                    1995 + (index % 30),
                    None,
                    "built-in-expanded",
                    f"{language.lower()}-song-{index + 1}",
                    50 + (index % 50),
                )
            )
        for index in range(50):
            title, tags, genre = MOVIE_MOODS[index % len(MOVIE_MOODS)]
            items.append(
                (
                    f"{language} {title} {index + 1}",
                    "movie",
                    language,
                    tags,
                    genre,
                    movie_creator,
                    1990 + (index % 35),
                    None,
                    "built-in-expanded",
                    f"{language.lower()}-movie-{index + 1}",
                    45 + (index % 55),
                )
            )
    return items


EXPANDED_SEED_ITEMS = generated_seed_items()
