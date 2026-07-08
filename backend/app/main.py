from fastapi import FastAPI

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