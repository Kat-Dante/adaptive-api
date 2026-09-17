from typing import Protocol, Any


class SourceAdapter(Protocol):
    """Defines how to interpret one source's pagination/envelope shape.

    A new source with a different response shape means implementing
    this Protocol, not modifying fetch_all_pages().
    """

    def extract_items(self, payload: Any) -> list[dict]:
        """Pull the list of raw record dicts out of a page's response body."""
        ...

    def has_more(self, payload: Any) -> bool:
        """Whether another page should be fetched."""
        ...

    def next_page_params(self, current_params: dict, payload: Any) -> dict:
        """Compute the query params for the next page request."""
        ...