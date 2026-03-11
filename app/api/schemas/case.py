from pydantic import BaseModel


class CaseCreate(BaseModel):
    member_id: str
    measure_type: str
    year: int
    current_pdc: float
