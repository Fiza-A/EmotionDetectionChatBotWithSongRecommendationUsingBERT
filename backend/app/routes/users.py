from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.user import PreferenceUpdate, UserPreferenceRead, UserRead
from app.services.user_service import update_preferences

router = APIRouter()


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/preferences", response_model=UserPreferenceRead)
def preferences(payload: PreferenceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prefs = update_preferences(db, current_user, payload.preferred_languages)
    return {"preferred_languages": prefs.preferred_languages.split(",")}
