from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.case import router as case_router
from app.persistence.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Q4 Rescue", lifespan=lifespan)

app.include_router(case_router)

@app.get("/health")
def health():
    return {"status": "ok"}
