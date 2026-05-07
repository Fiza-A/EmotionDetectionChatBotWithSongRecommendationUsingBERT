from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import MoodHistory, User
from app.schemas.chat import MoodHistoryRead

router = APIRouter()


@router.get("/history", response_model=list[MoodHistoryRead])
def mood_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(MoodHistory)
        .filter(MoodHistory.user_id == current_user.id)
        .order_by(MoodHistory.created_at.asc())
        .limit(300)
        .all()
    )
