"""
Orders Router

Per CLAUDE.md: Order management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderWithItems
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("")
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    source: Optional[str] = None,
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List orders with filters"""
    orders, total = OrderService.list_orders(
        db=db,
        brand_id=current_user.brand_id,
        customer_id=customer_id,
        status=status,
        channel=channel,
        source=source,
        campaign_id=campaign_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "total": total,
        "data": [OrderResponse.model_validate(o) for o in orders]
    }


@router.post("")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    order = OrderService.create_order(
        db=db,
        brand_id=current_user.brand_id,
        order_data=order_data
    )
    return OrderResponse.model_validate(order)


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order by ID"""
    order = OrderService.get_order_with_items(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify brand ownership
    if order.brand_id != current_user.brand_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderWithItems.model_validate(order)


@router.put("/{order_id}")
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an order"""
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.brand_id != current_user.brand_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_dict = order_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(order, field, value)
    
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.get("/customer/{customer_id}")
def get_customer_orders(
    customer_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get orders for a specific customer"""
    orders, total = OrderService.get_customer_orders(
        db=db,
        customer_id=customer_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "data": [OrderResponse.model_validate(o) for o in orders]
    }


@router.get("/{order_id}/timeline")
def get_order_timeline(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order with associated communications"""
    order = OrderService.get_order_with_items(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.brand_id != current_user.brand_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get communications for this order's customer
    from app.models.communication import Communication
    communications = db.query(Communication).filter(
        Communication.customer_id == order.customer_id
    ).order_by(Communication.sent_at.desc()).limit(20).all()
    
    return {
        "order": OrderWithItems.model_validate(order),
        "communications": [
            {
                "id": c.id,
                "channel": c.channel,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "sent_at": c.sent_at,
            }
            for c in communications
        ]
    }


@router.get("/stats/summary")
def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order statistics for the brand"""
    return OrderService.get_order_stats(db, current_user.brand_id)