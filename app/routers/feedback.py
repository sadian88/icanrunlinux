from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.feedback import FeedbackSubmit
from app.services.feedback import (
    get_feedback_for_session,
    get_history_by_ip,
    get_public_feedback,
    submit_feedback,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = getattr(request, "client", None)
    if client and hasattr(client, "host"):
        return client.host
    return request.headers.get("X-Real-IP", "127.0.0.1")


@router.post("")
def create_feedback(body: FeedbackSubmit, request: Request):
    ip = _get_client_ip(request)
    ok = submit_feedback(
        session_token=body.session_token,
        ip_address=ip,
        rating=body.rating,
        comment=body.comment,
    )
    if not ok:
        return JSONResponse(
            status_code=404,
            content={"error": "session_not_found", "message": "Search session not found."},
        )
    return {"status": "ok"}


@router.get("/history")
def get_history(request: Request, limit: int = 20):
    ip = _get_client_ip(request)
    sessions = get_history_by_ip(ip, limit=limit)
    return {"sessions": sessions, "ip": ip}


@router.get("/public")
def get_public(request: Request, limit: int = 50):
    items = get_public_feedback(limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/{session_token}")
def get_feedback(session_token: str):
    fb = get_feedback_for_session(session_token)
    if fb is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": "No feedback found for this session."},
        )
    return fb
