from fastapi import FastAPI

app = FastAPI(
    title="Bookies",
    description="Backend API for the Bookies Club Tracker",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Bookies Club API is running!"
    }