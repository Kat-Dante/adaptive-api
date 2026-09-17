from dataclasses import dataclass
from typing import Any

@dataclass
class Record:
    data: dict[str, Any]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
def aggregate(records: list[Record], primary_keys: list[str], sum_fields: list[str]) -> list[dict]:
        """Group records by primary_keys, summing sum_fields."""
        groups: dict[tuple, dict] = {}
        for record in records:
             key = tuple(record.get(pk) for pk in primary_keys)
             
             if key not in groups:
                 groups[key] = {pk: record.get(pk) for pk in primary_keys}
                 for field in sum_fields:
                     groups[key][field] = 0
                     
                 for field in sum_fields:
                    value = record.get(field)
                    if isinstance(value, (int, float)):
                        groups[key][field] += value

        return list(groups.values())