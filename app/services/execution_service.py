"""
Execution business logic. This is where the Rule Engine gets called
(Step 6) before an execution is persisted — the service layer is the
only thing that talks to both the rule engine and the repository.
"""

import uuid

from sqlalchemy.orm import Session

from app.rule_engine import engine as rule_engine
from app.repositories.execution_repository import ExecutionRepository
from app.schemas.execution import ExecutionCreate, ExecutionRead


class ExecutionService:
    def __init__(self, db: Session):
        self.repo = ExecutionRepository(db)

    def start_execution(self, data: ExecutionCreate) -> ExecutionRead:
        # Rule Engine (the whiteboard's decision node): if the caller
        # didn't explicitly pick a test_type, decide it from branch + event.
        if not data.test_type:
            decision = rule_engine.evaluate(data.branch, data.event)
            data.test_type = ",".join(decision.test_types)
        execution = self.repo.create(data)
        return ExecutionRead.model_validate(execution)

    def get_execution(self, execution_id: uuid.UUID) -> ExecutionRead | None:
        execution = self.repo.get_by_id(execution_id)
        return ExecutionRead.model_validate(execution) if execution else None

    def list_executions(self) -> list[ExecutionRead]:
        return [ExecutionRead.model_validate(e) for e in self.repo.list_all()]

    def finish_execution(self, execution_id: uuid.UUID, result: str) -> ExecutionRead | None:
        execution = self.repo.get_by_id(execution_id)
        if not execution:
            return None
        execution = self.repo.mark_finished(execution, result)
        return ExecutionRead.model_validate(execution)

    def apply_github_workflow_event(
        self, github_run_id: str, action: str, conclusion: str | None
    ) -> ExecutionRead | None:
        """
        Called by the webhook handler for `workflow_run` events.
        Correlates GitHub's event stream to our execution rows via run_id.
        """
        execution = self.repo.get_by_github_run_id(github_run_id)
        if not execution:
            return None
        if action in ("requested", "in_progress"):
            execution = self.repo.mark_started(execution)
        elif action == "completed":
            execution = self.repo.mark_finished(execution, conclusion or "unknown")
        return ExecutionRead.model_validate(execution)
