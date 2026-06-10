from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import json
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.segment import Segment
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.segment import (
    SegmentCreate, SegmentUpdate, SegmentResponse,
    SegmentPreviewRequest, SegmentPreviewResponse
)

router = APIRouter(prefix="/segments", tags=["Segments"])


def apply_segment_rules(db: Session, brand_id: int, rules: list) -> list:
    """Apply segment rules to filter customers"""
    query = db.query(Customer).filter(Customer.brand_id == brand_id)
    
    for rule in rules:
        field = rule.get("field")
        operator = rule.get("operator")
        value = rule.get("value")
        
        # Handle order-based fields with subquery
        if field in ["total_orders", "total_spent", "average_order_value", "days_since_last_order"]:
            # Create subquery for order aggregations
            if field == "total_orders":
                subquery = db.query(
                    Order.customer_id,
                    func.count(Order.id).label("total_orders")
                ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
                query = query.outerjoin(subquery, Customer.id == subquery.c.customer_id)
                
                if operator == "greater_than":
                    query = query.filter(subquery.c.total_orders > int(value))
                elif operator == "less_than":
                    query = query.filter(subquery.c.total_orders < int(value))
                elif operator == "equals":
                    query = query.filter(subquery.c.total_orders == int(value))
            
            elif field == "total_spent":
                subquery = db.query(
                    Order.customer_id,
                    func.sum(Order.total).label("total_spent")
                ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
                query = query.outerjoin(subquery, Customer.id == subquery.c.customer_id)
                
                if operator == "greater_than":
                    query = query.filter(subquery.c.total_spent > float(value))
                elif operator == "less_than":
                    query = query.filter(subquery.c.total_spent < float(value))
            
            elif field == "days_since_last_order":
                from datetime import datetime, timedelta
                days = int(value)
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                subquery = db.query(
                    Order.customer_id,
                    func.max(Order.order_date).label("last_order")
                ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
                query = query.outerjoin(subquery, Customer.id == subquery.c.customer_id)
                
                if operator == "greater_than":
                    query = query.filter(
                        (subquery.c.last_order < cutoff_date) | 
                        (subquery.c.last_order.is_(None))
                    )
        
        # Handle customer fields
        else:
            if field == "email":
                if operator == "contains":
                    query = query.filter(Customer.email.ilike(f"%{value}%"))
                elif operator == "equals":
                    query = query.filter(Customer.email == value)
                elif operator == "is_null":
                    query = query.filter(Customer.email.is_(None))
                elif operator == "is_not_null":
                    query = query.filter(Customer.email.isnot(None))
            
            elif field == "phone":
                if operator == "contains":
                    query = query.filter(Customer.phone.ilike(f"%{value}%"))
                elif operator == "is_null":
                    query = query.filter(Customer.phone.is_(None))
            
            elif field == "city":
                if operator == "contains":
                    query = query.filter(Customer.city.ilike(f"%{value}%"))
                elif operator == "equals":
                    query = query.filter(Customer.city == value)
            
            elif field == "state":
                if operator == "contains":
                    query = query.filter(Customer.state.ilike(f"%{value}%"))
                elif operator == "equals":
                    query = query.filter(Customer.state == value)
            
            elif field == "country":
                if operator == "equals":
                    query = query.filter(Customer.country == value)
            
            elif field == "gender":
                if operator == "equals":
                    query = query.filter(Customer.gender == value)
            
            elif field == "is_unsubscribed":
                query = query.filter(Customer.is_unsubscribed == (value == "true"))
            
            elif field == "engagement_score":
                if operator == "greater_than":
                    query = query.filter(Customer.engagement_score > int(value))
                elif operator == "less_than":
                    query = query.filter(Customer.engagement_score < int(value))
                elif operator == "equals":
                    query = query.filter(Customer.engagement_score == int(value))
    
    return query.all()


@router.get("")
def list_segments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Segment).filter(Segment.brand_id == current_user.brand_id)
    total = query.count()
    segments = query.order_by(Segment.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "data": [SegmentResponse.model_validate(s) for s in segments]
    }


@router.post("")
def create_segment(
    segment_data: SegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate rules JSON before using it
    try:
        rules = json.loads(segment_data.rules)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid rules JSON format")
    
    # Validate rules structure
    if not isinstance(rules, list):
        raise HTTPException(status_code=400, detail="Rules must be a list")
    
    for rule in rules:
        if not isinstance(rule, dict):
            raise HTTPException(status_code=400, detail="Each rule must be an object")
        if "field" not in rule or "operator" not in rule or "value" not in rule:
            raise HTTPException(status_code=400, detail="Each rule must have field, operator, and value")
    
    segment = Segment(
        brand_id=current_user.brand_id,
        **segment_data.model_dump()
    )
    db.add(segment)
    db.flush()
    
    # Calculate customer count using validated rules
    customers = apply_segment_rules(db, current_user.brand_id, rules)
    segment.customer_count = len(customers)
    
    db.commit()
    db.refresh(segment)
    return SegmentResponse.model_validate(segment)


@router.get("/{segment_id}")
def get_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    segment = db.query(Segment).filter(
        Segment.id == segment_id,
        Segment.brand_id == current_user.brand_id
    ).first()
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return SegmentResponse.model_validate(segment)


@router.put("/{segment_id}")
def update_segment(
    segment_id: int,
    segment_data: SegmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    segment = db.query(Segment).filter(
        Segment.id == segment_id,
        Segment.brand_id == current_user.brand_id
    ).first()
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    update_data = segment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(segment, field, value)
    
    # Recalculate customer count if rules changed
    if "rules" in update_data:
        rules = json.loads(update_data["rules"])
        customers = apply_segment_rules(db, current_user.brand_id, rules)
        segment.customer_count = len(customers)
    
    db.commit()
    db.refresh(segment)
    return SegmentResponse.model_validate(segment)


@router.delete("/{segment_id}")
def delete_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    segment = db.query(Segment).filter(
        Segment.id == segment_id,
        Segment.brand_id == current_user.brand_id
    ).first()
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    db.delete(segment)
    db.commit()
    return {"message": "Segment deleted successfully"}


@router.post("/{segment_id}/preview")
def preview_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    segment = db.query(Segment).filter(
        Segment.id == segment_id,
        Segment.brand_id == current_user.brand_id
    ).first()
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    rules = json.loads(segment.rules)
    customers = apply_segment_rules(db, current_user.brand_id, rules)
    
    sample = [
        {
            "id": c.id,
            "email": c.email,
            "phone": c.phone,
            "first_name": c.first_name,
            "last_name": c.last_name
        }
        for c in customers[:10]
    ]
    
    return SegmentPreviewResponse(
        customer_count=len(customers),
        sample_customers=sample
    )


@router.post("/preview")
def preview_segment_rules(
    request: SegmentPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rules = json.loads(request.rules)
    customers = apply_segment_rules(db, current_user.brand_id, rules)
    
    sample = [
        {
            "id": c.id,
            "email": c.email,
            "phone": c.phone,
            "first_name": c.first_name,
            "last_name": c.last_name
        }
        for c in customers[:10]
    ]
    
    return SegmentPreviewResponse(
        customer_count=len(customers),
        sample_customers=sample
    )