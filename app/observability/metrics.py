from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


_METRICS_ENABLED = True

_REQUEST_DURATION_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_SERVICE_DURATION_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
_DB_DURATION_BUCKETS = (0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)

HTTP_REQUESTS_TOTAL = Counter(
    "q4_rescue_http_requests_total",
    "Total HTTP requests handled by the service.",
    ("method", "route", "status_code"),
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "q4_rescue_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=_REQUEST_DURATION_BUCKETS,
)
SERVICE_OPERATION_DURATION_SECONDS = Histogram(
    "q4_rescue_service_operation_duration_seconds",
    "Service-layer operation duration in seconds.",
    ("operation",),
    buckets=_SERVICE_DURATION_BUCKETS,
)
DB_OPERATIONS_TOTAL = Counter(
    "q4_rescue_db_operations_total",
    "Database operations executed by the service.",
    ("operation", "outcome"),
)
DB_OPERATION_DURATION_SECONDS = Histogram(
    "q4_rescue_db_operation_duration_seconds",
    "Database operation duration in seconds.",
    ("operation",),
    buckets=_DB_DURATION_BUCKETS,
)
CASES_CREATED_TOTAL = Counter(
    "q4_rescue_cases_created_total",
    "Cases successfully created.",
)
CASE_CREATE_CONFLICTS_TOTAL = Counter(
    "q4_rescue_case_create_conflicts_total",
    "Case creation conflicts encountered by reason.",
    ("reason",),
)
CASE_STATUS_TRANSITIONS_TOTAL = Counter(
    "q4_rescue_case_status_transitions_total",
    "Case status transitions executed by destination status.",
    ("status",),
)
IDEMPOTENCY_REPLAYS_TOTAL = Counter(
    "q4_rescue_idempotency_replays_total",
    "Idempotent create requests replayed from cache.",
)


def configure_metrics(*, enabled: bool) -> None:
    global _METRICS_ENABLED
    _METRICS_ENABLED = enabled


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def record_http_request(*, method: str, route: str, status_code: int, duration_seconds: float) -> None:
    if not _METRICS_ENABLED:
        return

    status_code_label = str(status_code)
    HTTP_REQUESTS_TOTAL.labels(method=method, route=route, status_code=status_code_label).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route).observe(duration_seconds)


def record_service_operation(*, operation: str, duration_seconds: float) -> None:
    if not _METRICS_ENABLED:
        return

    SERVICE_OPERATION_DURATION_SECONDS.labels(operation=operation).observe(duration_seconds)


def record_db_operation(*, operation: str, outcome: str, duration_seconds: float) -> None:
    if not _METRICS_ENABLED:
        return

    DB_OPERATIONS_TOTAL.labels(operation=operation, outcome=outcome).inc()
    DB_OPERATION_DURATION_SECONDS.labels(operation=operation).observe(duration_seconds)


def increment_cases_created() -> None:
    if _METRICS_ENABLED:
        CASES_CREATED_TOTAL.inc()


def increment_case_create_conflict(*, reason: str) -> None:
    if _METRICS_ENABLED:
        CASE_CREATE_CONFLICTS_TOTAL.labels(reason=reason).inc()


def increment_case_status_transition(*, status: str) -> None:
    if _METRICS_ENABLED:
        CASE_STATUS_TRANSITIONS_TOTAL.labels(status=status).inc()


def increment_idempotency_replay() -> None:
    if _METRICS_ENABLED:
        IDEMPOTENCY_REPLAYS_TOTAL.inc()
