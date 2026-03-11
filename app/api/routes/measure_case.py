from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timezone

from app.api.schemas.measure_case import MeasureCaseCreate
from app.domain.measure_case import (
    MeasureCase,
    MeasureCaseStatus,
)
from app.persistence.db import get_conn
from app.persistence.repositories.measure_case_repo import MeasureCaseRepository
from app.persistence.repositories.idempotency_repo import IdempotencyRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

def get_measure_case_repo() -> MeasureCaseRepository:
    return MeasureCaseRepository(get_conn())


def get_idempotency_repo() -> IdempotencyRepository:
    return IdempotencyRepository(get_conn())


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CaseStatusUpdateSchema(BaseModel):
    status: Literal["open", "in_progress", "on_hold", "closed", "archived"]


# ---------------------------------------------------------------------------
# CREATE CASE
# ---------------------------------------------------------------------------

@router.post("/cases/", status_code=201)
def create_case(
    payload: MeasureCaseCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    repo: MeasureCaseRepository = Depends(get_measure_case_repo),
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
            detail="Active MeasureCase already exists for this member/measure/year",
        )

    case = MeasureCase.create(
        member_id=payload.member_id,
        measure_type=payload.measure_type,
        year=payload.year,
        current_pdc=payload.current_pdc,
    )

    repo.create(case)

    response = {
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

    if idempotency_key:
        idem_repo.save(route="POST:/cases", key=idempotency_key, response=response)

    return response


# ---------------------------------------------------------------------------
# LIST CASES
# ---------------------------------------------------------------------------

@router.get("/cases")
def list_cases(repo: MeasureCaseRepository = Depends(get_measure_case_repo)):
    cases = repo.list_all()

    return [
        {
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
        for case in cases
    ]


# ---------------------------------------------------------------------------
# GET CASE BY ID
# ---------------------------------------------------------------------------

@router.get("/cases/{case_id}")
def get_case(
    case_id: str,
    repo: MeasureCaseRepository = Depends(get_measure_case_repo),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case_id")

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="MeasureCase not found")

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


# ---------------------------------------------------------------------------
# UPDATE STATUS
# ---------------------------------------------------------------------------

@router.put("/cases/{case_id}/status")
def update_case_status(
    case_id: str,
    payload: CaseStatusUpdateSchema,
    repo: MeasureCaseRepository = Depends(get_measure_case_repo),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case_id")

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="MeasureCase not found")

    try:
        if payload.status == MeasureCaseStatus.IN_PROGRESS.value:
            case.start()

        elif payload.status == MeasureCaseStatus.ON_HOLD.value:
            case.hold()

        elif payload.status == MeasureCaseStatus.CLOSED.value:
            case.close()

        elif payload.status == MeasureCaseStatus.ARCHIVED.value:
            case.archive()

        elif payload.status == MeasureCaseStatus.OPEN.value:
            if case.status != MeasureCaseStatus.ON_HOLD:
                raise HTTPException(
                    status_code=400,
                    detail="Only ON_HOLD cases can be reopened to OPEN",
                )
            case.status = MeasureCaseStatus.OPEN
            case.updated_at = datetime.now(timezone.utc)

        else:
            raise HTTPException(status_code=400, detail="Invalid status")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    repo.update(case)

    return {
        "id": str(case.id.value),
        "status": case.status.value,
        "updated_at": case.updated_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# ARCHIVE (DELETE ENDPOINT)
# ---------------------------------------------------------------------------

@router.delete("/cases/{case_id}", status_code=204)
def archive_case(
    case_id: str,
    repo: MeasureCaseRepository = Depends(get_measure_case_repo),
):
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid case_id")

    case = repo.get_by_id(case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="MeasureCase not found")

    try:
        case.archive()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    repo.update(case)
