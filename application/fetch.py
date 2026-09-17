from infrastructure.pagination import fetch_all_pages
from domain.record import aggregate

async def fetch_and_aggregate(
    source_url: str,
    primary_keys: list[str],
    sum_fields: list[str],
) -> list[dict]:
    records = await fetch_all_pages(source_url)
    return aggregate(records, primary_keys, sum_fields)
