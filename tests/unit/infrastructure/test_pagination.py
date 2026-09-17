import pytest
import httpx
import respx
from fastapi import HTTPException
from infrastructure.pagination import fetch_all_pages

@pytest.mark.asyncio
@respx.mock
async def test_fetch_all_pages_raises_when_source_never_terminates():
    respx.get("https://fake-source.test/infinite").mock(
        return_value=httpx.Response(200, json={"items": [{"id": 1}], "has_more": True})
    )

    with pytest.raises(HTTPException) as exc_info:
        await fetch_all_pages("https://fake-source.test/infinite", max_pages=3)

    assert exc_info.value.status_code == 502
    assert "max_pages" in exc_info.value.detail

@pytest.mark.asyncio
@respx.mock
async def test_fetch_all_pages_handles_flat_array():
    respx.get("https://fake-source.test/flat").mock(
        return_value=httpx.Response(200, json=[{"id": 1}, {"id": 2}])
    )

    records = await fetch_all_pages("https://fake-source.test/flat")
    assert len(records) == 2