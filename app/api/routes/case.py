from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.schemas.case import CaseCreate
from app.domain.case import Case, CaseStatus
from app.persistence.db import get_conn
from app.persistence.repositories.case_repo import CaseRepository
from app.persistence.repositories.idempotency_repo import IdempotencyRepository

router = APIRouter()


def get_case_repo() -> CaseRepository:
    return CaseRepository(get_conn())


def get_idempotency_repo() -> IdempotencyRepository:
    return IdempotencyRepository(get_conn())


class CaseStatusUpdateSchema(BaseModel):
    status: Literal["open", "in_progress", "on_hold", "closed", "archived"]


def _serialize_case(case: Case) -> dict[str, str | int | float]:
    return {
        "id": str(case.id.value),
        "status": case.status.value,
        "member_id": case.member_id,
        "measure_type": case.measure_type,
        "year": case.year,
        "current_pdc": case.current_pdc,
        "target_pdc": case.target_pdc,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
    }


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

    if repo.exists_active_case(
        member_id=payload.member_id,
        measure_type=payload.measure_type,
        year=payload.year,
    ):
        raise HTTPException(
            status_code=409,
            detail="Active Case already exists for this member/measure/year",
        )

    case = Case.create(
        member_id=payload.member_id,
        measure_type=payload.measure_type,
        year=payload.year,
        current_pdc=payload.current_pdc,
    )
    repo.create(case)

    response = _serialize_case(case)

    if idempotency_key:
        idem_repo.save(route="POST:/cases", key=idempotency_key, response=response)

    return response


@router.get("/cases")
def list_cases(repo: CaseRepository = Depends(get_case_repo)):
    return [_serialize_case(case) for case in repo.list_all()]


@router.get("/cases/{case_id}")
def get_case(case_id: str, repo: CaseRepository = Depends(get_case_repo)):
    try:
        case_uuid = UUID(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid case_id") from exc

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return _serialize_case(case)


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
            case.close()
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
