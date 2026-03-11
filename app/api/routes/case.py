import sqlite3
from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db_conn
from app.api.schemas.case import CaseCreate
from app.domain.case import CaseStatus
from app.domain.errors import ConflictError, ValidationError
from app.persistence.repositories.case_repo import CaseRepository
from app.persistence.repositories.idempotency_repo import IdempotencyRepository

router = APIRouter()


def get_case_repo(conn: sqlite3.Connection = Depends(get_db_conn)) -> CaseRepository:
    return CaseRepository(conn)


def get_idempotency_repo(
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> IdempotencyRepository:
    return IdempotencyRepository(conn)


class CaseStatusUpdateSchema(BaseModel):
    status: Literal["open", "in_progress", "on_hold", "closed", "archived"]
    closed_reason: str | None = None


@router.post("/cases/", status_code=201)
def create_case(
    payload: CaseCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    repo: CaseRepository = Depends(get_case_repo),
    idem_repo: IdempotencyRepository = Depends(get_idempotency_repo),
):
    if idempotency_key:
        cached = idem_repo.get(route="POST:/cases", key=idempotency_key)
        if cached:
            return cached

    if repo.exists_active_case(payload.member.health_plan_member_id):
        raise HTTPException(status_code=409, detail="Active Case already exists for this member")

    try:
        response = repo.create(payload.model_dump(mode="python"))
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if idempotency_key:
        idem_repo.save(route="POST:/cases", key=idempotency_key, response=response)

    return response


@router.get("/cases")
def list_cases(repo: CaseRepository = Depends(get_case_repo)):
    return repo.list_all()


@router.get("/cases/{case_id}")
def get_case(case_id: str, repo: CaseRepository = Depends(get_case_repo)):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return repo.get_case_graph(case_uuid)


@router.put("/cases/{case_id}/status")
def update_case_status(
    case_id: str,
    payload: CaseStatusUpdateSchema,
    repo: CaseRepository = Depends(get_case_repo),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        if payload.status == CaseStatus.IN_PROGRESS.value:
            case.start()
        elif payload.status == CaseStatus.ON_HOLD.value:
            case.hold()
        elif payload.status == CaseStatus.CLOSED.value:
            case.close(closed_reason=payload.closed_reason)
        elif payload.status == CaseStatus.ARCHIVED.value:
            case.archive()
        elif payload.status == CaseStatus.OPEN.value:
            case.reopen(now=datetime.now(timezone.utc))
        else:
            raise HTTPException(status_code=400, detail="Invalid status")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repo.update(case)

    return {
        "id": str(case.id.value),
        "status": case.status.value,
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "archived_at": case.archived_at.isoformat() if case.archived_at else None,
        "updated_at": case.updated_at.isoformat(),
    }


@router.delete("/cases/{case_id}", status_code=204)
def archive_case(
    case_id: str,
    repo: CaseRepository = Depends(get_case_repo),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        case.archive()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repo.update(case)
