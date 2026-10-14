from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, subscriptions, dashboard

app = FastAPI(title="Subscription & Expense Tracker")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(dashboard.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}