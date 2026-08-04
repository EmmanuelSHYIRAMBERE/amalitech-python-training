from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import database
from models import (
    OrderCreate,
    OrderItemCreate,
    OrderItemResponse,
    OrderResponse,
    OrderStatus,
    OrderUpdate,
    PaginatedOrders,
)
from fastapi import HTTPException

_VALID_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.pending: [OrderStatus.confirmed, OrderStatus.cancelled],
    OrderStatus.confirmed: [OrderStatus.shipped, OrderStatus.cancelled],
    OrderStatus.shipped: [OrderStatus.delivered],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: [],
}

_UNDELETABLE_STATUSES = {OrderStatus.shipped, OrderStatus.delivered}


def _compute_items(raw: list[OrderItemCreate]) -> tuple[list[OrderItemResponse], float]:
    items: list[OrderItemResponse] = []
    total = 0.0
    for item in raw:
        subtotal = round(item.quantity * item.unit_price, 2)
        total += subtotal
        items.append(
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=subtotal,
            )
        )
    return items, round(total, 2)


def get_or_404(order_id: int) -> OrderResponse:
    order = database._db.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


def create_order(body: OrderCreate) -> OrderResponse:
    items, total_price = _compute_items(body.items)
    now = datetime.now(timezone.utc)

    order = OrderResponse(
        id=database._next_id,
        customer_id=body.customer_id,
        status=OrderStatus.pending,
        items=items,
        total_price=total_price,
        shipping_address=body.shipping_address,
        notes=body.notes,
        created_at=now,
        updated_at=now,
    )
    database._db[database._next_id] = order
    database._next_id += 1
    return order


def list_orders(
    skip: int,
    limit: int,
    status: Optional[OrderStatus],
    customer_id: Optional[int],
) -> PaginatedOrders:
    orders = list(database._db.values())

    if status is not None:
        orders = [o for o in orders if o.status == status]
    if customer_id is not None:
        orders = [o for o in orders if o.customer_id == customer_id]

    total = len(orders)
    page = orders[skip : skip + limit]

    return PaginatedOrders(total=total, skip=skip, limit=limit, items=page)


def get_order(order_id: int) -> OrderResponse:
    return get_or_404(order_id)


def update_order(order_id: int, body: OrderUpdate) -> OrderResponse:
    order = get_or_404(order_id)

    if body.status not in _VALID_TRANSITIONS[order.status]:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition from '{order.status}' to '{body.status}'",
        )

    if body.shipping_address is not None and order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=409,
            detail="Shipping address can only be updated while the order is pending",
        )

    updated = order.model_copy(
        update={
            "status": body.status,
            "shipping_address": body.shipping_address or order.shipping_address,
            "notes": body.notes if body.notes is not None else order.notes,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    database._db[order_id] = updated
    return updated


def delete_order(order_id: int) -> None:
    order = get_or_404(order_id)

    if order.status in _UNDELETABLE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete an order with status '{order.status}'",
        )

    del database._db[order_id]
