from fastapi import FastAPI
from app.persistence.db import init_db
from app.api.routes.measure_case import router as measure_case_router

app = FastAPI(title="Q4 Rescue")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(measure_case_router)

@app.get("/health")
def health():
    return {"status": "ok"}
