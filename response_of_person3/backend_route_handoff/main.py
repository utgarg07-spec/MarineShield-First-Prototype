from fastapi import FastAPI
from backend.api import router

app = FastAPI(title="MarineShield API", version="0.1.0-dev")
app.include_router(router.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "SYNTHETIC_DEVELOPMENT_FIXTURE"}
