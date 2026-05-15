from fastapi import APIRouter

from app.models.distro import RecommendRequest, RecommendResult
from app.services.matching import find_compatible_hybrid

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post("", response_model=list[RecommendResult])
def recommend(req: RecommendRequest):
    results = find_compatible_hybrid(
        ram_gb=req.ram_gb,
        storage_gb=req.storage_gb,
        use_cases=req.use_cases or None,
        architecture=req.architecture,
        difficulty=req.difficulty,
        free_text=req.free_text,
        limit=req.limit,
    )
    return results
