"""Initial schema

Revision ID: 20260314_0001
Revises:
Create Date: 2026-03-14 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.persistence.sql import load_schema_sql, split_sql_script


# revision identifiers, used by Alembic.
revision = "20260314_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for statement in split_sql_script(load_schema_sql()):
        op.execute(sa.text(statement))


def downgrade() -> None:
    for table_name in (
        "idempotency_keys",
        "audit_events",
        "task_contact_attempts",
        "contact_attempts",
        "tasks",
        "barriers",
        "medication_pharmacy_refills",
        "medication_pharmacies",
        "medication_providers",
        "pharmacies",
        "providers",
        "medications",
        "measures",
        "cases",
        "referrals",
        "members",
    ):
        op.execute(sa.text(f"DROP TABLE IF EXISTS {table_name}"))
