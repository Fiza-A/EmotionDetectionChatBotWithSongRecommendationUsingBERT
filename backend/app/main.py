from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.routes import auth, chat, conversations, mood, recommendations, users


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(mood.router, prefix="/mood", tags=["mood"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
