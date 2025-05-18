from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from home_task.db import get_session
from fastapi.responses import JSONResponse

router = APIRouter()

QUERY = """
    SELECT standard_job_id,
           country_code,
           min_days_to_hire,
           average_days_to_hire,
           max_days_to_hire,
           num_postings
    FROM public.days_to_hire_statistics
    WHERE standard_job_id = :standard_job_id
      AND country_code IS NOT DISTINCT FROM :country_code
"""


@router.get("/stats/days-to-hire")
def get_days_to_hire_statistics(
    standard_job_id: str = Query(..., description="Standard job ID"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"),
):

    with get_session() as session:
        result = session.execute(QUERY, {"standard_job_id": standard_job_id, "country_code": country_code}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Statistics not found")

    return JSONResponse(
        {
            "standard_job_id": result.standard_job_id,
            "country_code": result.country_code,
            "min_days_to_hire": result.min_days_to_hire,
            "average_days_to_hire": result.average_days_to_hire,
            "max_days_to_hire": result.max_days_to_hire,
            "num_postings": result.num_postings,
        }
    )
