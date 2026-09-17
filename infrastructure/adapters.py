from typing import Any


class EnvelopeAdapter:
    """For sources returning {"items": [...], "has_more": bool}."""

    def extract_items(self, payload: Any) -> list[dict]:
        if isinstance(payload, dict):
            return payload.get("items", [])
        return []

    def has_more(self, payload: Any) -> bool:
        return isinstance(payload, dict) and payload.get("has_more", False)

    def next_page_params(self, current_params: dict, payload: Any) -> dict:
        return {**current_params, "page": current_params.get("page", 1) + 1}


class FlatListAdapter:
    """For sources returning a bare JSON array with no pagination envelope."""

    def extract_items(self, payload: Any) -> list[dict]:
        return payload if isinstance(payload, list) else []

    def has_more(self, payload: Any) -> bool:
        return False

    def next_page_params(self, current_params: dict, payload: Any) -> dict:
        return current_params


def detect_adapter(payload: Any):
    """Pick the right adapter based on the shape of the first response.

    This is the one place that still branches on shape — everywhere
    else now depends only on the SourceAdapter interface.
    """
    if isinstance(payload, list):
        return FlatListAdapter()
    return EnvelopeAdapter()