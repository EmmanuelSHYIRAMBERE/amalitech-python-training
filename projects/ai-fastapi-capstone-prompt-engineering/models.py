from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=100)
    unit_price: float = Field(..., gt=0.0)


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float


class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: list[OrderItemCreate] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)


class OrderUpdate(BaseModel):
    status: OrderStatus
    shipping_address: Optional[str] = Field(None, min_length=10, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    items: list[OrderItemResponse]
    total_price: float
    shipping_address: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class PaginatedOrders(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[OrderResponse]
