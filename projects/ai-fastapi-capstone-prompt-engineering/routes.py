from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Path, Query

import services
from models import OrderCreate, OrderResponse, OrderStatus, OrderUpdate, PaginatedOrders

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201, summary="Create a new order")
def create_order(body: OrderCreate) -> OrderResponse:
    return services.create_order(body)


@router.get("", response_model=PaginatedOrders, summary="Retrieve a paginated list of orders")
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    customer_id: Optional[int] = Query(None, gt=0),
) -> PaginatedOrders:
    return services.list_orders(skip, limit, status, customer_id)


@router.get("/{order_id}", response_model=OrderResponse, summary="Retrieve a single order by ID")
def get_order(order_id: int = Path(..., gt=0)) -> OrderResponse:
    return services.get_order(order_id)


@router.patch("/{order_id}", response_model=OrderResponse, summary="Update order status or details")
def update_order(order_id: int = Path(..., gt=0), body: OrderUpdate = ...) -> OrderResponse:
    return services.update_order(order_id, body)


@router.delete("/{order_id}", status_code=204, summary="Cancel and delete an order")
def delete_order(order_id: int = Path(..., gt=0)) -> None:
    services.delete_order(order_id)
