from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth

app = FastAPI(title="Subscription & Expense Tracker")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}