from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


_TRACING_CONFIGURED = False


def configure_tracing(
    *,
    enabled: bool,
    service_name: str,
    service_version: str,
    environment: str,
    otlp_endpoint: str | None,
    otlp_headers: dict[str, str],
) -> None:
    global _TRACING_CONFIGURED

    if _TRACING_CONFIGURED or not enabled:
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        }
    )
    provider = TracerProvider(resource=resource)

    resolved_endpoint = (otlp_endpoint or "").strip()
    if resolved_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=resolved_endpoint,
            headers=otlp_headers,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    _TRACING_CONFIGURED = True


def get_tracer(name: str):
    return trace.get_tracer(name)
