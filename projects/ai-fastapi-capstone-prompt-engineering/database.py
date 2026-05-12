from __future__ import annotations

from models import OrderResponse

_db: dict[int, OrderResponse] = {}
_next_id: int = 1
