from fastapi import FastAPI

app = FastAPI(title="Subscription & Expense Tracker")

@app.get("/health")
def health_check():
    return {"status": "healthy"}