import httpx
from fastapi import HTTPException
from domain.record import Record
from infrastructure.adapters import detect_adapter


async def fetch_all_pages(
    base_url: str,
    params: dict | None = None,
    max_pages: int = 1000,
) -> list[Record]:
    params = dict(params or {})
    params.setdefault("page", 1)
    params.setdefault("page_size", 100)

    all_records: list[Record] = []
    pages_fetched = 0
    adapter = None

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            if pages_fetched >= max_pages:
                raise HTTPException(
                    status_code=502,
                    detail=f"Source exceeded max_pages ({max_pages}) without terminating: {base_url}",
                )

            try:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
            except httpx.ConnectError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Could not reach source_url: {base_url}",
                ) from exc
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Source returned {exc.response.status_code}: {base_url}",
                ) from exc

            try:
                payload = response.json()
            except ValueError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Source did not return valid JSON: {base_url}",
                ) from exc

            if adapter is None:
                adapter = detect_adapter(payload)

            items = adapter.extract_items(payload)
            all_records.extend(Record(data=item) for item in items)
            pages_fetched += 1

            if not adapter.has_more(payload) or not items:
                break

            params = adapter.next_page_params(params, payload)

    return all_records