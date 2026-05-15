from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.distro import RecommendRequest
from app.services.feedback import generate_session_token, save_search_history
from app.services.matching import find_compatible_hybrid
from app.services.validator import validate_hardware_query

router = APIRouter(prefix="/recommend", tags=["recommend"])


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = getattr(request, "client", None)
    if client and hasattr(client, "host"):
        return client.host
    return request.headers.get("X-Real-IP", "127.0.0.1")


@router.post("")
def recommend(req: RecommendRequest, request: Request):
    ip = _get_client_ip(request)

    # Validate free_text against hardware keywords
    if req.free_text:
        valid, sanitized = validate_hardware_query(req.free_text)
        if not valid:
            return JSONResponse(
                status_code=422,
                content={"error": "invalid_input", "message": sanitized},
            )
        req.free_text = sanitized

    results = find_compatible_hybrid(
        ram_gb=req.ram_gb,
        storage_gb=req.storage_gb,
        use_cases=req.use_cases or None,
        architecture=req.architecture,
        difficulty=req.difficulty,
        free_text=req.free_text,
        limit=req.limit,
    )

    session_token = generate_session_token()
    request_data = {
        "free_text": req.free_text,
        "use_cases": req.use_cases,
        "ram_gb": req.ram_gb,
        "storage_gb": req.storage_gb,
        "architecture": req.architecture,
        "difficulty": req.difficulty,
        "limit": req.limit,
    }
    save_search_history(session_token, ip, request_data)

    return {
        "session_token": session_token,
        "results": results,
    }
