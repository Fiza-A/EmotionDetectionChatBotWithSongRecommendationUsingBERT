from app.models.models import Recommendation
from app.services.recommendation_service import recommendation_to_read


def test_recommendation_tags_are_returned_as_list():
    item = Recommendation(
        id=1,
        title="Test",
        type="song",
        language="English",
        mood_tags="uplifting,hopeful",
        genre="Pop",
    )
    assert recommendation_to_read(item)["mood_tags"] == ["uplifting", "hopeful"]
