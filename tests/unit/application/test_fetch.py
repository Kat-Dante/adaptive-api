import pytest
from domain.record import Record
from application.fetch import fetch_and_aggregate

@pytest.mark.asyncio
async def test_fetch_and_aggregate_orchestrates_fetch_then_aggregate(monkeypatch):
    fake_records = [
        Record(data={"customer_id": "A", "total_amount": 50}),
        Record(data={"customer_id": "A", "total_amount": 30}),
    ]

    async def fake_fetch_all_pages(source_url, params=None):
        return fake_records

    monkeypatch.setattr(
        "application.fetch.fetch_all_pages",
        fake_fetch_all_pages,
    )

    result = await fetch_and_aggregate(
        source_url="https://irrelevant.test/anything",
        primary_keys=["customer_id"],
        sum_fields=["total_amount"],
    )

    assert result == [{"customer_id": "A", "total_amount": 80}]