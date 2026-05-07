from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import create_access_token
from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.user_service import authenticate_user, create_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = create_user(db, payload)
    return {"access_token": create_access_token(str(user.id)), "user": user}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    return {"access_token": create_access_token(str(user.id)), "user": user}
