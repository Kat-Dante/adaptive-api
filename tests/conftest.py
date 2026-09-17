import pytest
import httpx
import respx

@pytest.fixture
def orders_payload_page1():
    return {
        "items": [
            {"customer_id": "A", "total_amount": 50},
            {"customer_id": "B", "total_amount": 20},
        ],
        "has_more": True,
    }

@pytest.fixture
def orders_payload_page2():
    return {
        "items": [{"customer_id": "A", "total_amount": 30}],
        "has_more": False,
    }