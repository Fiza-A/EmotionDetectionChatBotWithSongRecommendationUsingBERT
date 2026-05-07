from app.services.itunes_service import ITunesTrack, itunes_fields_for


def test_itunes_fields_shape_when_no_track(monkeypatch):
    monkeypatch.setattr("app.services.itunes_service.search_music", lambda title, artist: None)
    assert itunes_fields_for("Missing", "Artist") == {
        "preview_url": None,
        "album_art": None,
        "external_url": None,
    }


def test_itunes_fields_shape_when_track_found(monkeypatch):
    monkeypatch.setattr(
        "app.services.itunes_service.search_music",
        lambda title, artist: ITunesTrack(
            title="Happy",
            artist="Pharrell Williams",
            preview_url="https://example.com/preview.m4a",
            album_art="https://example.com/art.jpg",
            external_url="https://music.apple.com/example",
            score=1.0,
        ),
    )
    assert itunes_fields_for("Happy", "Pharrell Williams")["preview_url"].endswith(".m4a")
