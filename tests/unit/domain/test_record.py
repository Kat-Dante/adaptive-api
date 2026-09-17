from domain.record import Record, aggregate

def test_aggregate_sums_single_field_by_single_key():
    records = [
        Record(data={"customer_id": "A", "total_amount": 50}),
        Record(data={"customer_id": "A", "total_amount": 30}),
        Record(data={"customer_id": "B", "total_amount": 20}),
    ]
    result = aggregate(records, primary_keys=["customer_id"], sum_fields=["total_amount"])
    result_by_key = {r["customer_id"]: r["total_amount"] for r in result}
    assert result_by_key == {"A": 80, "B": 20}

def test_aggregate_empty_input_returns_empty_list():
    result = aggregate([], primary_keys=["customer_id"], sum_fields=["total_amount"])
    assert result == []