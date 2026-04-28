from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.git_client import GitOperationError
from app.trigger_handler import prepare_manual_trigger_payload

router = APIRouter(tags=["trigger"])


class TriggerRequest(BaseModel):
    repo_url: str
    branch: str


@router.post("/trigger")
async def trigger_pipeline(payload: TriggerRequest) -> dict[str, Any]:
    try:
        return prepare_manual_trigger_payload(payload.repo_url, payload.branch)
    except GitOperationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository preparation failed: {exc}",
        ) from exc
