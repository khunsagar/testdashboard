"""
Execution endpoints. This is Step 5 — the first real vertical slice
through the whole stack: api -> service -> repository -> model -> db.

Once this works, uncomment the include_router lines in app/main.py.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.execution import ExecutionCreate, ExecutionFinish, ExecutionRead
from app.services.execution_service import ExecutionService

router = APIRouter()


@router.post("/start", response_model=ExecutionRead)
def start_execution(payload: ExecutionCreate, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    return service.start_execution(payload)


@router.get("/{execution_id}", response_model=ExecutionRead)
def get_execution(execution_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    execution = service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/{execution_id}/finish", response_model=ExecutionRead)
def finish_execution(
    execution_id: uuid.UUID, payload: ExecutionFinish, db: Session = Depends(get_db)
):
    """The 'Notify Finish' step in every GitHub workflow calls this."""
    service = ExecutionService(db)
    execution = service.finish_execution(execution_id, payload.result)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/", response_model=list[ExecutionRead])
def list_executions(db: Session = Depends(get_db)):
    service = ExecutionService(db)
    return service.list_executions()
