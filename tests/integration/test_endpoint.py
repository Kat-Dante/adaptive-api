import httpx
import respx
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@respx.mock
def test_aggregate_endpoint_sums_orders_across_pages():
    respx.get(
        "https://fake-source.test/orders", params={"page": "1", "page_size": "100"}
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {"customer_id": "A", "total_amount": 50},
                    {"customer_id": "B", "total_amount": 20},
                ],
                "has_more": True,
            },
        )
    )
    respx.get(
        "https://fake-source.test/orders", params={"page": "2", "page_size": "100"}
    ).mock(
        return_value=httpx.Response(
            200,
            json={"items": [{"customer_id": "A", "total_amount": 30}], "has_more": False},
        )
    )

    response = client.get(
        "/aggregate",
        params={
            "source_url": "https://fake-source.test/orders",
            "primary_keys": "customer_id",
            "sum_fields": "total_amount",
        },
    )

    assert response.status_code == 200
    body = response.json()
    result_by_key = {r["customer_id"]: r["total_amount"] for r in body["results"]}
    assert result_by_key == {"A": 80, "B": 20}

@respx.mock
def test_get_raw_data_returns_all_records_unfiltered():
    respx.get(
        "https://fake-source.test/orders", params={"page": "1", "page_size": "100"}
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {"customer_id": "A", "total_amount": 50},
                    {"customer_id": "B", "total_amount": 20},
                ],
                "has_more": False,
            },
        )
    )

    response = client.get("/data", params={"source_url": "https://fake-source.test/orders"})

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    
@respx.mock
def test_aggregate_endpoint_returns_raw_data_when_keys_omitted():
    respx.get(
        "https://fake-source.test/orders", params={"page": "1", "page_size": "100"}
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {"customer_id": "A", "total_amount": 50},
                    {"customer_id": "B", "total_amount": 20},
                ],
                "has_more": False,
            },
        )
    )

    response = client.get(
        "/aggregate",
        params={"source_url": "https://fake-source.test/orders"},
    )
    
    assert response.status_code == 200
    body = response.json()
    assert body["aggregated"] is False
    assert body["count"] == 2