from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.case import router as case_router
from app.observability.http import instrument_app
from app.observability.logging import configure_logging
from app.observability.metrics import configure_metrics
from app.observability.tracing import configure_tracing
from app.persistence.db import init_db
from app.settings import get_settings, validate_runtime_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_runtime_settings()
    init_db()
    yield


settings = get_settings()
configure_logging(
    service_name=settings.service_name,
    environment=settings.environment,
    log_level=settings.log_level,
)
configure_metrics(enabled=settings.metrics_enabled)
configure_tracing(
    enabled=settings.otel_enabled,
    service_name=settings.service_name,
    service_version=settings.service_version,
    environment=settings.environment,
    otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    otlp_headers=settings.otel_exporter_otlp_headers,
)

app = FastAPI(
    title="Q4 Rescue",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

instrument_app(app, metrics_enabled=settings.metrics_enabled)
app.include_router(case_router)


@app.get("/health")
def health():
    return {"status": "ok"}
