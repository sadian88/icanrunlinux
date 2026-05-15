from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Benchmark(BaseModel):
    test_name: str
    score: float
    unit: str = ""
    source_url: str = ""


class PackageStats(BaseModel):
    total_packages: int = 0
    outdated_packages: int = 0
    vulnerable_packages: int = 0
    newest_packages: int = 0
    problematic_packages: int = 0
    source_url: str = ""


class DistroOut(BaseModel):
    id: int
    slug: str
    url: str
    name: str
    based_on: list[str]
    origin: Optional[str] = None
    architecture: list[str]
    desktop: list[str]
    category: list[str]
    status: Optional[str] = None
    latest_version: Optional[str] = None
    description: Optional[str] = None
    popularity_rank: Optional[int] = None
    hits_per_day: Optional[int] = None
    use_cases: list[str]
    difficulty: int
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    recommended_for: list[str]
    architectures: list[str]
    package_manager: Optional[str] = None
    init_system: Optional[str] = None
    release_model: Optional[str] = None
    technical_notes: Optional[str] = None
    benchmarks: list[Benchmark] = []
    package_stats: Optional[PackageStats] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecommendRequest(BaseModel):
    ram_gb: Optional[int] = Field(default=None, ge=0, le=1024)
    storage_gb: Optional[int] = Field(default=None, ge=0, le=10240)
    use_cases: list[str] = Field(default_factory=list, max_length=10)
    architecture: Optional[str] = Field(default=None, max_length=50)
    difficulty: Optional[list[int]] = Field(default=None, max_length=5)
    free_text: Optional[str] = Field(default=None, max_length=1000)
    limit: int = Field(default=10, ge=1, le=20)

    model_config = {"extra": "forbid"}


class RecommendResult(BaseModel):
    distro: DistroOut
    similarity: float
    source: str = "database"
    ai_reason: Optional[str] = None


class AiDistroSuggestion(BaseModel):
    name: str
    slug: str
    description: str
    based_on: list[str] = []
    origin: Optional[str] = None
    architectures: list[str] = []
    desktop: list[str] = []
    category: list[str] = []
    difficulty: int = 3
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    use_cases: list[str] = []
    recommended_for: list[str] = []
    package_manager: str = ""
    init_system: str = ""
    release_model: str = ""
    technical_notes: str = ""
    why: str
