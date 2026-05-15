from typing import Optional

from fastapi import APIRouter, Query

from app.models.distro import DistroOut
from app.services.db import dict_row, get_conn

router = APIRouter(prefix="/distros", tags=["distros"])


@router.get("", response_model=list[DistroOut])
def list_distros(
    slug: Optional[str] = Query(None),
    difficulty: Optional[list[int]] = Query(None),
    use_case: Optional[list[str]] = Query(None, alias="use_case"),
    architecture: Optional[str] = Query(None),
    min_ram: Optional[int] = Query(None),
    max_ram: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    conn = get_conn()
    cur = conn.cursor()

    conditions: list[str] = []
    params: list = []

    if slug:
        conditions.append("slug = %s")
        params.append(slug)

    if difficulty:
        placeholders = ", ".join(["%s" for _ in difficulty])
        conditions.append(f"difficulty IN ({placeholders})")
        params.extend(difficulty)

    if use_case:
        uc_conds = " OR ".join(["%s = ANY(use_cases)" for _ in use_case])
        conditions.append(f"({uc_conds})")
        params.extend(use_case)

    if architecture:
        conditions.append("%s = ANY(architectures)")
        params.append(architecture)

    if min_ram is not None:
        conditions.append("(min_ram_gb IS NULL OR min_ram_gb >= %s)")
        params.append(min_ram)

    if max_ram is not None:
        conditions.append("(min_ram_gb IS NULL OR min_ram_gb <= %s)")
        params.append(max_ram)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT * FROM distros
        {where_clause}
        ORDER BY popularity_rank ASC NULLS LAST
        LIMIT %s
    """
    params.append(limit)
    cur.execute(query, params)
    rows = [dict_row(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
