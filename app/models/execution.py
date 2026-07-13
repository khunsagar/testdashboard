"""
Execution model — the core table from the whiteboard's `workflow_run` design.

This is the ONE model to build first (Step 4). Everything else
(Project, Repository, Runner, TestResult, Artifact...) follows the same
pattern once this vertical slice works end to end.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Uuid

from app.db.base import Base


class Execution(Base):
    __tablename__ = "executions"

    # sqlalchemy.Uuid is dialect-agnostic: native UUID on Postgres,
    # CHAR(32) on the SQLite placeholder DB. Works on both.
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_run_id = Column(String, nullable=True, index=True)
    workflow_name = Column(String, nullable=True)
    repository = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    commit_sha = Column(String, nullable=True)
    event = Column(String, nullable=True)  # push / pull_request / workflow_dispatch / schedule
    actor = Column(String, nullable=True)
    trigger_type = Column(String, nullable=True)  # manual / scheduled / github_action
    test_type = Column(String, nullable=True)  # smoke / regression / api / e2e
    status = Column(String, default="queued")  # queued / in_progress / completed
    result = Column(String, nullable=True)  # success / failure / cancelled / timed_out
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
