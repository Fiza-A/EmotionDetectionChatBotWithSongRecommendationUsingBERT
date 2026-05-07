import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


@dataclass
class ITunesTrack:
    title: str
    artist: str
    preview_url: str | None
    album_art: str | None
    external_url: str | None
    score: float


def _clean(value: str | None) -> str:
    return (value or "").lower().replace("&", "and").strip()


def _score_result(title: str, artist: str | None, result: dict) -> float:
    expected = f"{_clean(title)} {_clean(artist)}".strip()
    actual = f"{_clean(result.get('trackName'))} {_clean(result.get('artistName'))}".strip()
    title_score = SequenceMatcher(None, _clean(title), _clean(result.get("trackName"))).ratio()
    combined_score = SequenceMatcher(None, expected, actual).ratio() if expected else 0
    preview_bonus = 0.08 if result.get("previewUrl") else 0
    return max(title_score, combined_score) + preview_bonus


def search_music(title: str, artist: str | None = None, country: str = "US", limit: int = 5, timeout: int = 12) -> ITunesTrack | None:
    query = quote_plus(" ".join(part for part in [title, artist] if part))
    url = f"{ITUNES_SEARCH_URL}?term={query}&media=music&entity=song&limit={limit}&country={country}"
    request = Request(url, headers={"User-Agent": "EmotionDetectionChatbot/1.0"})

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    candidates = [item for item in payload.get("results", []) if item.get("kind") == "song"]
    if not candidates:
        return None
    best = max(candidates, key=lambda item: _score_result(title, artist, item))
    return ITunesTrack(
        title=best.get("trackName") or title,
        artist=best.get("artistName") or artist or "",
        preview_url=best.get("previewUrl"),
        album_art=best.get("artworkUrl100"),
        external_url=best.get("trackViewUrl"),
        score=_score_result(title, artist, best),
    )


def itunes_fields_for(title: str, artist: str | None) -> dict[str, str | None]:
    track = search_music(title, artist)
    if not track:
        return {"preview_url": None, "album_art": None, "external_url": None}
    return {
        "preview_url": track.preview_url,
        "album_art": track.album_art,
        "external_url": track.external_url,
    }
