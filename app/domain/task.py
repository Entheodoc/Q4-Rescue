from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class TaskId:
    value: UUID

    @staticmethod
    def new() -> "TaskId":
        return TaskId(uuid4())


@dataclass
class Task:
    id: TaskId
    case_id: UUID
    task_type: str
    title: str
    status: TaskStatus
    priority: str | None
    related_measure_ids: tuple[UUID, ...]
    related_medication_ids: tuple[UUID, ...]
    barrier_id: UUID | None
    description: str | None
    due_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    outcome: str | None
    assigned_to: str | None
    assigned_queue: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        case_id: UUID,
        task_type: str,
        title: str,
        related_measure_ids: tuple[UUID, ...] = (),
        related_medication_ids: tuple[UUID, ...] = (),
        barrier_id: UUID | None = None,
        priority: str | None = None,
        description: str | None = None,
        due_at: datetime | None = None,
        assigned_to: str | None = None,
        assigned_queue: str | None = None,
        now: datetime | None = None,
    ) -> "Task":
        now = now or datetime.now(timezone.utc)

        if not task_type or not task_type.strip():
            raise ValidationError("task_type is required")

        if not title or not title.strip():
            raise ValidationError("title is required")

        return Task(
            id=TaskId.new(),
            case_id=case_id,
            task_type=task_type.strip(),
            title=title.strip(),
            status=TaskStatus.OPEN,
            priority=priority.strip() if priority and priority.strip() else None,
            related_measure_ids=tuple(related_measure_ids),
            related_medication_ids=tuple(related_medication_ids),
            barrier_id=barrier_id,
            description=description.strip() if description and description.strip() else None,
            due_at=due_at,
            completed_at=None,
            cancelled_at=None,
            outcome=None,
            assigned_to=assigned_to.strip() if assigned_to and assigned_to.strip() else None,
            assigned_queue=assigned_queue.strip() if assigned_queue and assigned_queue.strip() else None,
            created_at=now,
            updated_at=now,
        )
