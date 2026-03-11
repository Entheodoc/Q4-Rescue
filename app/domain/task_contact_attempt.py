from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TaskContactAttemptId:
    value: UUID

    @staticmethod
    def new() -> "TaskContactAttemptId":
        return TaskContactAttemptId(uuid4())


@dataclass
class TaskContactAttempt:
    id: TaskContactAttemptId
    task_id: UUID
    contact_attempt_id: UUID
    effect_on_task: str | None
    notes: str | None
    created_at: datetime

    @staticmethod
    def create(
        *,
        task_id: UUID,
        contact_attempt_id: UUID,
        effect_on_task: str | None = None,
        notes: str | None = None,
        now: datetime | None = None,
    ) -> "TaskContactAttempt":
        now = now or datetime.now(timezone.utc)

        return TaskContactAttempt(
            id=TaskContactAttemptId.new(),
            task_id=task_id,
            contact_attempt_id=contact_attempt_id,
            effect_on_task=effect_on_task.strip() if effect_on_task and effect_on_task.strip() else None,
            notes=notes.strip() if notes and notes.strip() else None,
            created_at=now,
        )
