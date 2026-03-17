from __future__ import annotations

from contextvars import ContextVar

from opentelemetry import trace


_request_id: ContextVar[str | None] = ContextVar("q4_request_id", default=None)
_actor_subject: ContextVar[str | None] = ContextVar("q4_actor_subject", default=None)


def bind_request_id(request_id: str | None) -> None:
    _request_id.set(request_id)


def bind_actor_subject(actor_subject: str | None) -> None:
    _actor_subject.set(actor_subject)


def clear_context() -> None:
    _request_id.set(None)
    _actor_subject.set(None)


def get_request_id() -> str | None:
    return _request_id.get()


def get_actor_subject() -> str | None:
    return _actor_subject.get()


def get_trace_context() -> tuple[str | None, str | None]:
    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return None, None
    return (
        format(span_context.trace_id, "032x"),
        format(span_context.span_id, "016x"),
    )


def build_log_context() -> dict[str, str]:
    context: dict[str, str] = {}

    request_id = get_request_id()
    if request_id:
        context["request_id"] = request_id

    actor_subject = get_actor_subject()
    if actor_subject:
        context["actor_subject"] = actor_subject

    trace_id, span_id = get_trace_context()
    if trace_id:
        context["trace_id"] = trace_id
    if span_id:
        context["span_id"] = span_id

    return context
