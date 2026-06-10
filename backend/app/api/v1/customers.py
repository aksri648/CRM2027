from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerWithStats, CustomerImportRequest
)

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_customer_stats(db: Session, customer_id: int) -> dict:
    """Calculate customer statistics from orders"""
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    total_orders = len(orders)
    total_spent = sum(o.total for o in orders)
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0
    last_order_date = max((o.order_date for o in orders), default=None)
    
    return {
        "total_orders": total_orders,
        "total_spent": total_spent,
        "average_order_value": avg_order_value,
        "last_order_date": last_order_date
    }


@router.get("")
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    has_email: Optional[bool] = None,
    is_unsubscribed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Customer).filter(Customer.brand_id == current_user.brand_id)
    
    if search:
        query = query.filter(
            (Customer.email.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%")) |
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%"))
        )
    
    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Customer.state.ilike(f"%{state}%"))
    if has_email is not None:
        if has_email:
            query = query.filter(Customer.email.isnot(None))
        else:
            query = query.filter(Customer.email.is_(None))
    if is_unsubscribed is not None:
        query = query.filter(Customer.is_unsubscribed == is_unsubscribed)
    
    total = query.count()
    customers = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [CustomerResponse.model_validate(c) for c in customers]
    }


@router.post("")
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = Customer(
        brand_id=current_user.brand_id,
        **customer_data.model_dump()
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.brand_id == current_user.brand_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    stats = get_customer_stats(db, customer_id)
    response = CustomerWithStats(
        **CustomerResponse.model_validate(customer).model_dump(),
        **stats
    )
    return response


@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.brand_id == current_user.brand_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.brand_id == current_user.brand_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


@router.get("/{customer_id}/timeline")
def get_customer_timeline(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.brand_id == current_user.brand_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get customer orders
    orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()
    
    timeline = []
    for order in orders:
        timeline.append({
            "type": "order",
            "id": order.id,
            "title": f"Order #{order.order_number}",
            "description": f"₹{order.total} - {order.status}",
            "date": order.order_date
        })
    
    # Sort by date descending
    timeline.sort(key=lambda x: x["date"] if x["date"] else "", reverse=True)
    
    return {
        "customer_id": customer_id,
        "timeline": timeline
    }


@router.post("/import")
def import_customers(
    request: CustomerImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    imported = 0
    errors = []
    
    for i, customer_data in enumerate(request.customers):
        try:
            customer = Customer(
                brand_id=current_user.brand_id,
                **customer_data.model_dump()
            )
            db.add(customer)
            imported += 1
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    db.commit()
    
    return {
        "imported": imported,
        "total": len(request.customers),
        "errors": errors if errors else None
    }