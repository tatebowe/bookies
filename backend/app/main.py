from fastapi import FastAPI
from app.database.database import engine, Base

from app.models import user
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookies API",
    description="Backend API for managing book clubs",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Bookies!",
        "status": "API is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

app.include_router(users.router)