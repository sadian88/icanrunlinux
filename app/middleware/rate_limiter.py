from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import RATE_LIMIT_MAX, RATE_LIMIT_WINDOW


class _RateLimitStore:
    def __init__(self) -> None:
        self._records: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        with self._lock:
            window_start = now - RATE_LIMIT_WINDOW
            self._records[ip] = [t for t in self._records[ip] if t > window_start]
            if len(self._records[ip]) >= RATE_LIMIT_MAX:
                return False
            self._records[ip].append(now)
            return True

    def remaining(self, ip: str) -> int:
        now = time.time()
        with self._lock:
            window_start = now - RATE_LIMIT_WINDOW
            self._records[ip] = [t for t in self._records[ip] if t > window_start]
            return max(0, RATE_LIMIT_MAX - len(self._records[ip]))

    def reset_for(self, ip: str) -> None:
        with self._lock:
            self._records.pop(ip, None)


_store = _RateLimitStore()


def get_rate_limit_store() -> _RateLimitStore:
    return _store


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = getattr(request, "client", None)
    if client and hasattr(client, "host"):
        return client.host
    return request.headers.get("X-Real-IP", "127.0.0.1")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/recommend":
            ip = _get_client_ip(request)
            if not _store.is_allowed(ip):
                retry_after = RATE_LIMIT_WINDOW
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Too many requests. Max {RATE_LIMIT_MAX} per {RATE_LIMIT_WINDOW}s.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
        response = await call_next(request)
        return response
