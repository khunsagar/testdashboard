"""
Data access layer for Execution. Only DB queries live here — no business
logic, no rule evaluation. Services call this; this never calls services.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate


class ExecutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ExecutionCreate) -> Execution:
        execution = Execution(**data.model_dump())
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_by_id(self, execution_id: uuid.UUID) -> Execution | None:
        return self.db.query(Execution).filter(Execution.id == execution_id).first()

    def list_all(self, limit: int = 50) -> list[Execution]:
        return self.db.query(Execution).order_by(Execution.created_at.desc()).limit(limit).all()

    def get_by_github_run_id(self, github_run_id: str) -> Execution | None:
        return (
            self.db.query(Execution)
            .filter(Execution.github_run_id == github_run_id)
            .first()
        )

    def mark_started(self, execution: Execution) -> Execution:
        execution.status = "in_progress"
        execution.started_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def mark_finished(self, execution: Execution, result: str) -> Execution:
        execution.status = "completed"
        execution.result = result
        execution.finished_at = datetime.utcnow()
        if execution.started_at is None:
            execution.started_at = execution.created_at
        self.db.commit()
        self.db.refresh(execution)
        return execution
