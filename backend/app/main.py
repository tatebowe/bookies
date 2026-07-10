from fastapi import FastAPI

from app.database.database import Base, engine

# Import ALL models before create_all
from app.routers import auth, clubs, users

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookies API",
    description="Backend API for managing book clubs",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Tome-Tet!",
        "status": "API is running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(clubs.router)
