from fastapi import APIRouter, Query
from application.fetch import fetch_and_aggregate
from infrastructure.pagination import fetch_all_pages

router = APIRouter()

@router.get("/aggregate")
async def get_aggregated_data(
    source_url: str = Query(..., description="External JSON endpoint to pull from"),
    primary_keys: list[str] | None = Query(
        None, description="Fields to group by (omit to skip aggregation)"
    ),
    sum_fields: list[str] | None = Query(
        None, description="Numeric fields to sum (omit to skip aggregation)"
    ),
):
    if not primary_keys or not sum_fields:
        records = await fetch_all_pages(source_url)
        results = [record.data for record in records]
        return {"count": len(results), "results": results, "aggregated": False}


    result = await fetch_and_aggregate(source_url, primary_keys, sum_fields)
    return {"count": len(result), "results": result, "aggregated": True}

@router.get("/data")
async def get_raw_data(
    source_url: str = Query(..., description="External JSON endpoint to pull from"),
):
    records = await fetch_all_pages(source_url)
    results = [record.data for record in records]
    return {"count": len(results), "results": results}