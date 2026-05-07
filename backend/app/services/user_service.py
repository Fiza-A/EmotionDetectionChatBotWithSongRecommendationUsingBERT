from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models.models import User, UserPreference
from app.schemas.auth import LoginRequest, RegisterRequest


def serialize_languages(languages: list[str]) -> str:
    return ",".join(dict.fromkeys([language.strip() for language in languages if language.strip()]))


def parse_languages(value: str | None) -> list[str]:
    if not value:
        return ["English"]
    return [language.strip() for language in value.split(",") if language.strip()]


def create_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.query(User).filter(or_(User.email == payload.email, User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username is already registered.")
    user = User(username=payload.username, email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(UserPreference(user_id=user.id, preferred_languages=serialize_languages(payload.preferred_languages)))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return user


def update_preferences(db: Session, user: User, languages: list[str]) -> UserPreference:
    prefs = user.preferences or UserPreference(user_id=user.id)
    prefs.preferred_languages = serialize_languages(languages)
    db.add(prefs)
    db.commit()
    db.refresh(prefs)
    return prefs
