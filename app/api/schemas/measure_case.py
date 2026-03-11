from pydantic import BaseModel


class MeasureCaseCreate(BaseModel):
    member_id: str
    measure_type: str
    year: int
    current_pdc: float | None = None
