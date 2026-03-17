from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from opentelemetry.trace import Status, StatusCode

from app.observability.context import bind_request_id, clear_context, get_trace_context
from app.observability.metrics import record_http_request, render_metrics
from app.observability.tracing import get_tracer


LOGGER = logging.getLogger(__name__)
TRACER = get_tracer(__name__)
_EXCLUDED_PATHS = frozenset({"/health", "/metrics"})


def _resolve_route_template(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path or request.url.path


def _should_record_request(route_template: str) -> bool:
    return route_template not in _EXCLUDED_PATHS


def instrument_app(app: FastAPI, *, metrics_enabled: bool) -> None:
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", "").strip() or str(uuid4())
        request.state.request_id = request_id
        bind_request_id(request_id)

        start_time = perf_counter()
        status_code = 500
        route_template = request.url.path

        with TRACER.start_as_current_span("http.server.request") as span:
            span.set_attribute("http.request.method", request.method)
            span.set_attribute("url.path", request.url.path)
            span.set_attribute("q4.request_id", request_id)

            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as exc:
                route_template = _resolve_route_template(request)
                duration_seconds = perf_counter() - start_time

                span.update_name(f"{request.method} {route_template}")
                span.set_attribute("http.route", route_template)
                span.set_attribute("http.response.status_code", status_code)
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))

                if metrics_enabled and _should_record_request(route_template):
                    record_http_request(
                        method=request.method,
                        route=route_template,
                        status_code=status_code,
                        duration_seconds=duration_seconds,
                    )

                if _should_record_request(route_template):
                    LOGGER.exception(
                        "HTTP request failed",
                        extra={
                            "event": "http.request",
                            "http_method": request.method,
                            "route": route_template,
                            "status_code": status_code,
                            "duration_ms": round(duration_seconds * 1000, 2),
                        },
                    )

                clear_context()
                raise

            route_template = _resolve_route_template(request)
            duration_seconds = perf_counter() - start_time
            trace_id, _ = get_trace_context()

            span.update_name(f"{request.method} {route_template}")
            span.set_attribute("http.route", route_template)
            span.set_attribute("http.response.status_code", response.status_code)
            if response.status_code >= 500:
                span.set_status(Status(StatusCode.ERROR))

            response.headers["X-Request-ID"] = request_id
            if trace_id:
                response.headers["X-Trace-ID"] = trace_id

            if metrics_enabled and _should_record_request(route_template):
                record_http_request(
                    method=request.method,
                    route=route_template,
                    status_code=response.status_code,
                    duration_seconds=duration_seconds,
                )

            if _should_record_request(route_template):
                log_method = LOGGER.warning if response.status_code >= 500 else LOGGER.info
                log_method(
                    "HTTP request completed",
                    extra={
                        "event": "http.request",
                        "http_method": request.method,
                        "route": route_template,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_seconds * 1000, 2),
                    },
                )

            clear_context()
            return response

    if metrics_enabled:
        @app.get("/metrics", include_in_schema=False)
        def metrics() -> Response:
            content, media_type = render_metrics()
            return Response(content=content, media_type=media_type)
