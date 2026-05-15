from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.security import RequestSizeLimitMiddleware, SecurityHeadersMiddleware
from app.routers import distros, feedback, recommend

origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

app = FastAPI(
    title="I Can Run Linux API",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimiterMiddleware)

app.include_router(distros.router)
app.include_router(recommend.router)
app.include_router(feedback.router)
