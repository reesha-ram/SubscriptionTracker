from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status

from app.routers import auth, subscriptions, dashboard

app = FastAPI(title="Subscription & Expense Tracker")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(dashboard.router)

@app.get("/", include_in_schema=False)
def root(request: Request):
    """
    Redirect root visitors:
    - If already logged in (cookie present), go directly to /dashboard/
    - Otherwise, go to /auth/login-page
    """
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard/", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
