from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db_conn, get_request_id
from app.api.schemas.case import CaseCreate
from app.api.security import AuthContext, require_permissions
from app.application.services.case_service import CaseService
from app.persistence.connection import DatabaseConnection
from app.persistence.repositories.audit_repo import AuditLogRepository
from app.persistence.repositories.case_repo import CaseRepository
from app.persistence.repositories.idempotency_repo import IdempotencyRepository

router = APIRouter()


def get_case_service(conn: DatabaseConnection = Depends(get_db_conn)) -> CaseService:
    return CaseService(
        case_repo=CaseRepository(conn),
        idempotency_repo=IdempotencyRepository(conn),
        audit_repo=AuditLogRepository(conn),
    )


class CaseStatusUpdateSchema(BaseModel):
    status: Literal["open", "in_progress", "on_hold", "closed", "archived"]
    closed_reason: str | None = None


@router.post("/cases/", status_code=201)
def create_case(
    payload: CaseCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    request_id: str = Depends(get_request_id),
    actor: AuthContext = Depends(require_permissions("cases:write")),
    service: CaseService = Depends(get_case_service),
):
    return service.create_case(
        payload=payload.model_dump(mode="python", exclude_unset=True),
        idempotency_key=idempotency_key,
        actor=actor,
        request_id=request_id,
    )


@router.get("/cases")
def list_cases(
    request_id: str = Depends(get_request_id),
    actor: AuthContext = Depends(require_permissions("cases:read")),
    service: CaseService = Depends(get_case_service),
):
    return service.list_case_summaries(actor=actor, request_id=request_id)


@router.get("/cases/{case_id}")
def get_case(
    case_id: str,
    request_id: str = Depends(get_request_id),
    actor: AuthContext = Depends(require_permissions("cases:detail")),
    service: CaseService = Depends(get_case_service),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    return service.get_case_detail(case_id=case_uuid, actor=actor, request_id=request_id)


@router.put("/cases/{case_id}/status")
def update_case_status(
    case_id: str,
    payload: CaseStatusUpdateSchema,
    request_id: str = Depends(get_request_id),
    actor: AuthContext = Depends(require_permissions("cases:write")),
    service: CaseService = Depends(get_case_service),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    return service.update_case_status(
        case_id=case_uuid,
        status=payload.status,
        closed_reason=payload.closed_reason,
        actor=actor,
        request_id=request_id,
    )


@router.delete("/cases/{case_id}", status_code=204)
def archive_case(
    case_id: str,
    request_id: str = Depends(get_request_id),
    actor: AuthContext = Depends(require_permissions("cases:write")),
    service: CaseService = Depends(get_case_service),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    service.archive_case(case_id=case_uuid, actor=actor, request_id=request_id)
