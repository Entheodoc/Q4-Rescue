from __future__ import annotations

import logging
from time import perf_counter
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from opentelemetry.trace import Status, StatusCode

from app.api.security import AuthContext
from app.domain.case import CaseStatus
from app.domain.errors import ConflictError, ValidationError
from app.observability.metrics import (
    increment_case_create_conflict,
    increment_case_status_transition,
    increment_cases_created,
    increment_idempotency_replay,
    record_service_operation,
)
from app.observability.tracing import get_tracer
from app.persistence.repositories.audit_repo import AuditLogRepository
from app.persistence.repositories.case_repo import CaseRepository
from app.persistence.repositories.idempotency_repo import IdempotencyRepository


LOGGER = logging.getLogger(__name__)
TRACER = get_tracer(__name__)


class CaseService:
    def __init__(
        self,
        *,
        case_repo: CaseRepository,
        idempotency_repo: IdempotencyRepository,
        audit_repo: AuditLogRepository,
    ):
        self.case_repo = case_repo
        self.idempotency_repo = idempotency_repo
        self.audit_repo = audit_repo

    def create_case(
        self,
        *,
        payload: dict,
        idempotency_key: str | None,
        actor: AuthContext,
        request_id: str,
    ) -> dict:
        start_time = perf_counter()

        with TRACER.start_as_current_span("case_service.create_case") as span:
            span.set_attribute("enduser.id", actor.subject)
            span.set_attribute("q4.request_id", request_id)
            span.set_attribute("q4.idempotency_key_present", bool(idempotency_key))

            try:
                if idempotency_key:
                    cached = self.idempotency_repo.get(route="POST:/cases", key=idempotency_key)
                    if cached:
                        increment_idempotency_replay()
                        span.set_attribute("q4.case.id", cached["id"])
                        span.set_attribute("q4.result", "idempotency_replay")
                        self._record_audit_event(
                            action="case.create.replayed",
                            resource_id=cached["id"],
                            actor=actor,
                            request_id=request_id,
                            metadata={"idempotency_key_present": True},
                        )
                        LOGGER.info(
                            "Replayed case create request from idempotency cache",
                            extra={
                                "event": "case.create.replayed",
                                "case_id": cached["id"],
                            },
                        )
                        return cached

                member_id = payload["member"]["health_plan_member_id"]
                span.set_attribute("q4.member.health_plan_member_id", member_id)

                if self.case_repo.exists_active_case(member_id):
                    increment_case_create_conflict(reason="active_case_exists")
                    span.set_attribute("q4.result", "conflict")
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=409, detail="Active Case already exists for this member")

                try:
                    response = self.case_repo.create(payload)
                except ValidationError as exc:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=422, detail=str(exc)) from exc
                except ConflictError as exc:
                    increment_case_create_conflict(reason="repository_conflict")
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=409, detail=str(exc)) from exc

                if idempotency_key:
                    self.idempotency_repo.save(
                        route="POST:/cases",
                        key=idempotency_key,
                        response=response,
                    )

                increment_cases_created()
                span.set_attribute("q4.case.id", response["id"])
                span.set_attribute("q4.result", "created")
                self._record_audit_event(
                    action="case.create",
                    resource_id=response["id"],
                    actor=actor,
                    request_id=request_id,
                    metadata={"idempotency_key_present": bool(idempotency_key)},
                )

                LOGGER.info(
                    "Created case",
                    extra={
                        "event": "case.create",
                        "case_id": response["id"],
                        "member_health_plan_member_id": member_id,
                    },
                )
                return response
            finally:
                record_service_operation(
                    operation="create_case",
                    duration_seconds=perf_counter() - start_time,
                )

    def list_case_summaries(self, *, actor: AuthContext, request_id: str) -> list[dict]:
        start_time = perf_counter()

        with TRACER.start_as_current_span("case_service.list_case_summaries") as span:
            span.set_attribute("enduser.id", actor.subject)
            span.set_attribute("q4.request_id", request_id)

            try:
                summaries = self.case_repo.list_summaries()
                span.set_attribute("q4.result", "listed")
                span.set_attribute("q4.result_count", len(summaries))
                self._record_audit_event(
                    action="case.list",
                    resource_id=None,
                    actor=actor,
                    request_id=request_id,
                    metadata={"result_count": len(summaries)},
                )
                return summaries
            finally:
                record_service_operation(
                    operation="list_case_summaries",
                    duration_seconds=perf_counter() - start_time,
                )

    def get_case_detail(self, *, case_id: UUID, actor: AuthContext, request_id: str) -> dict:
        start_time = perf_counter()

        with TRACER.start_as_current_span("case_service.get_case_detail") as span:
            span.set_attribute("enduser.id", actor.subject)
            span.set_attribute("q4.request_id", request_id)
            span.set_attribute("q4.case.id", str(case_id))

            try:
                case = self.case_repo.get_by_id(case_id)
                if not case:
                    span.set_attribute("q4.result", "not_found")
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=404, detail="Case not found")

                case_detail = self.case_repo.get_case_graph(case_id)
                span.set_attribute("q4.result", "found")
                self._record_audit_event(
                    action="case.detail.read",
                    resource_id=str(case_id),
                    actor=actor,
                    request_id=request_id,
                )
                return case_detail
            finally:
                record_service_operation(
                    operation="get_case_detail",
                    duration_seconds=perf_counter() - start_time,
                )

    def update_case_status(
        self,
        *,
        case_id: UUID,
        status: str,
        closed_reason: str | None,
        actor: AuthContext,
        request_id: str,
    ) -> dict:
        start_time = perf_counter()

        with TRACER.start_as_current_span("case_service.update_case_status") as span:
            span.set_attribute("enduser.id", actor.subject)
            span.set_attribute("q4.request_id", request_id)
            span.set_attribute("q4.case.id", str(case_id))
            span.set_attribute("q4.case.target_status", status)

            try:
                case = self.case_repo.get_by_id(case_id)
                if not case:
                    span.set_attribute("q4.result", "not_found")
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=404, detail="Case not found")

                try:
                    if status == CaseStatus.IN_PROGRESS.value:
                        case.start()
                    elif status == CaseStatus.ON_HOLD.value:
                        case.hold()
                    elif status == CaseStatus.CLOSED.value:
                        case.close(closed_reason=closed_reason)
                    elif status == CaseStatus.ARCHIVED.value:
                        case.archive()
                    elif status == CaseStatus.OPEN.value:
                        case.reopen(now=datetime.now(timezone.utc))
                    else:
                        span.set_attribute("q4.result", "invalid_status")
                        span.set_status(Status(StatusCode.ERROR))
                        raise HTTPException(status_code=400, detail="Invalid status")
                except HTTPException:
                    raise
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=400, detail=str(exc)) from exc

                self.case_repo.update(case)
                span.set_attribute("q4.result", "updated")
                increment_case_status_transition(status=case.status.value)
                self._record_audit_event(
                    action="case.status.update",
                    resource_id=str(case_id),
                    actor=actor,
                    request_id=request_id,
                    metadata={"status": case.status.value},
                )

                LOGGER.info(
                    "Updated case status",
                    extra={
                        "event": "case.status.update",
                        "case_id": str(case_id),
                        "status": case.status.value,
                    },
                )

                return {
                    "id": str(case.id.value),
                    "status": case.status.value,
                    "closed_at": case.closed_at.isoformat() if case.closed_at else None,
                    "archived_at": case.archived_at.isoformat() if case.archived_at else None,
                    "updated_at": case.updated_at.isoformat(),
                }
            finally:
                record_service_operation(
                    operation="update_case_status",
                    duration_seconds=perf_counter() - start_time,
                )

    def archive_case(self, *, case_id: UUID, actor: AuthContext, request_id: str) -> None:
        start_time = perf_counter()

        with TRACER.start_as_current_span("case_service.archive_case") as span:
            span.set_attribute("enduser.id", actor.subject)
            span.set_attribute("q4.request_id", request_id)
            span.set_attribute("q4.case.id", str(case_id))

            try:
                case = self.case_repo.get_by_id(case_id)
                if not case:
                    span.set_attribute("q4.result", "not_found")
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=404, detail="Case not found")

                try:
                    case.archive()
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(status_code=400, detail=str(exc)) from exc

                self.case_repo.update(case)
                span.set_attribute("q4.result", "archived")
                increment_case_status_transition(status=case.status.value)
                self._record_audit_event(
                    action="case.archive",
                    resource_id=str(case_id),
                    actor=actor,
                    request_id=request_id,
                    metadata={"status": case.status.value},
                )
                LOGGER.info(
                    "Archived case",
                    extra={
                        "event": "case.archive",
                        "case_id": str(case_id),
                        "status": case.status.value,
                    },
                )
            finally:
                record_service_operation(
                    operation="archive_case",
                    duration_seconds=perf_counter() - start_time,
                )

    def _record_audit_event(
        self,
        *,
        action: str,
        resource_id: str | None,
        actor: AuthContext,
        request_id: str,
        metadata: dict | None = None,
    ) -> None:
        self.audit_repo.record(
            action=action,
            resource_type="case",
            resource_id=resource_id,
            actor_subject=actor.subject,
            actor_permissions=list(actor.permissions),
            request_id=request_id,
            metadata=metadata,
        )
        self.case_repo.conn.commit()
