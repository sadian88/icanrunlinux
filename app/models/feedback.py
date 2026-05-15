from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FeedbackSubmit(BaseModel):
    session_token: str = Field(min_length=1, max_length=64)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)

    model_config = {"extra": "forbid"}


class FeedbackOut(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    created_at: Optional[str] = None
    search_query: Optional[str] = None


class SearchHistoryOut(BaseModel):
    session_token: str
    request_data: Optional[dict] = None
    created_at: Optional[str] = None
    feedback: Optional[FeedbackOut] = None


class HistoryListOut(BaseModel):
    sessions: list[SearchHistoryOut]
    ip: str


class RecommendResponse(BaseModel):
    session_token: str
    results: list


class ValidationError(BaseModel):
    error: str
    message: str
