"""
Customer Service - Business logic for customer operations

Per CLAUDE.md responsibilities:
- Create Customers
- Update Customers
- Customer Search
- Customer Import
- Customer Statistics
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json

from app.models.customer import Customer, CustomerChannel
from app.models.order import Order
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    
    @staticmethod
    def create_customer(db: Session, brand_id: int, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        customer = Customer(
            brand_id=brand_id,
            email=customer_data.email,
            phone=customer_data.phone,
            first_name=customer_data.first_name,
            last_name=customer_data.last_name,
            gender=customer_data.gender,
            date_of_birth=customer_data.date_of_birth,
            city=customer_data.city,
            state=customer_data.state,
            country=customer_data.country,
            postal_code=customer_data.postal_code,
            preferred_channel=customer_data.preferred_channel or CustomerChannel.EMAIL,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def update_customer(db: Session, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        """Update an existing customer"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(Customer.id == customer_id).first()
    
    @staticmethod
    def get_customer_with_orders(db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer with orders loaded"""
        return db.query(Customer).options(
            joinedload(Customer.orders)
        ).filter(Customer.id == customer_id).first()
    
    @staticmethod
    def search_customers(
        db: Session,
        brand_id: int,
        query: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        has_email: Optional[bool] = None,
        has_phone: Optional[bool] = None,
        is_unsubscribed: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Customer], int]:
        """
        Search customers with filters
        
        Returns: (customers, total_count)
        """
        q = db.query(Customer).filter(Customer.brand_id == brand_id)
        
        # Text search
        if query:
            search_filter = or_(
                Customer.email.ilike(f"%{query}%"),
                Customer.phone.ilike(f"%{query}%"),
                Customer.first_name.ilike(f"%{query}%"),
                Customer.last_name.ilike(f"%{query}%"),
            )
            q = q.filter(search_filter)
        
        # Filters
        if city:
            q = q.filter(Customer.city.ilike(f"%{city}%"))
        if state:
            q = q.filter(Customer.state.ilike(f"%{state}%"))
        if has_email is True:
            q = q.filter(Customer.email.isnot(None))
        elif has_email is False:
            q = q.filter(Customer.email.is_(None))
        if has_phone is True:
            q = q.filter(Customer.phone.isnot(None))
        elif has_phone is False:
            q = q.filter(Customer.phone.is_(None))
        if is_unsubscribed is not None:
            q = q.filter(Customer.is_unsubscribed == is_unsubscribed)
        
        # Get total count
        total = q.count()
        
        # Apply pagination
        customers = q.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
        
        return customers, total
    
    @staticmethod
    def get_customer_stats(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Calculate customer statistics
        
        Per CLAUDE.md:
        - ltv computed
        - total_orders computed
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {}
        
        # Get orders
        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        total_orders = len(orders)
        
        # Calculate LTV (Lifetime Value)
        total_spent = sum(order.total for order in orders) if orders else 0
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0
        
        # Last order date
        last_order_date = max((order.order_date for order in orders), default=None)
        
        # Days since last order
        days_since_last_order = None
        if last_order_date:
            days_since_last_order = (datetime.utcnow() - last_order_date).days
        
        return {
            "customer_id": customer_id,
            "total_orders": total_orders,
            "total_spent": total_spent,
            "average_order_value": avg_order_value,
            "last_order_date": last_order_date,
            "days_since_last_order": days_since_last_order,
            "engagement_score": customer.engagement_score,
            "is_unsubscribed": customer.is_unsubscribed,
        }
    
    @staticmethod
    def get_customer_timeline(db: Session, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get customer activity timeline
        
        Includes orders and communications
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return []
        
        timeline = []
        
        # Add orders
        orders = db.query(Order).filter(
            Order.customer_id == customer_id
        ).order_by(Order.order_date.desc()).limit(limit).all()
        
        for order in orders:
            timeline.append({
                "type": "order",
                "id": order.id,
                "date": order.order_date,
                "data": {
                    "order_number": order.order_number,
                    "total": order.total,
                    "status": order.status,
                    "channel": order.channel,
                }
            })
        
        # Add communications
        from app.models.communication import Communication
        comms = db.query(Communication).filter(
            Communication.customer_id == customer_id
        ).order_by(Communication.sent_at.desc()).limit(limit).all()
        
        for comm in comms:
            timeline.append({
                "type": "communication",
                "id": comm.id,
                "date": comm.sent_at,
                "data": {
                    "channel": comm.channel,
                    "status": comm.status,
                    "message": comm.content[:100] if comm.content else None,
                }
            })
        
        # Sort by date descending
        timeline.sort(key=lambda x: x["date"] or datetime.min, reverse=True)
        
        return timeline[:limit]
    
    @staticmethod
    def import_customers(db: Session, brand_id: int, customers_data: List[CustomerCreate]) -> int:
        """
        Bulk import customers
        
        Returns: count of imported customers
        """
        imported_count = 0
        
        for customer_data in customers_data:
            # Check for existing customer by email or phone
            existing = None
            if customer_data.email:
                existing = db.query(Customer).filter(
                    Customer.brand_id == brand_id,
                    Customer.email == customer_data.email
                ).first()
            
            if not existing and customer_data.phone:
                existing = db.query(Customer).filter(
                    Customer.brand_id == brand_id,
                    Customer.phone == customer_data.phone
                ).first()
            
            if existing:
                # Update existing customer
                for field in ['first_name', 'last_name', 'city', 'state', 'gender']:
                    value = getattr(customer_data, field, None)
                    if value:
                        setattr(existing, field, value)
            else:
                # Create new customer
                customer = Customer(
                    brand_id=brand_id,
                    email=customer_data.email,
                    phone=customer_data.phone,
                    first_name=customer_data.first_name,
                    last_name=customer_data.last_name,
                    gender=customer_data.gender,
                    city=customer_data.city,
                    state=customer_data.state,
                    country=customer_data.country,
                    postal_code=customer_data.postal_code,
                    preferred_channel=customer_data.preferred_channel or CustomerChannel.EMAIL,
                )
                db.add(customer)
                imported_count += 1
        
        db.commit()
        return imported_count
    
    @staticmethod
    def update_engagement_score(db: Session, customer_id: int, delta: int) -> Optional[Customer]:
        """
        Update customer engagement score
        
        Args:
            delta: Amount to add/subtract from score
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        customer.engagement_score = max(0, (customer.engagement_score or 0) + delta)
        customer.last_engaged_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def unsubscribe(db: Session, customer_id: int) -> Optional[Customer]:
        """Unsubscribe customer from communications"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        customer.is_unsubscribed = True
        customer.unsubscribed_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def resubscribe(db: Session, customer_id: int) -> Optional[Customer]:
        """Resubscribe customer to communications"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        customer.is_unsubscribed = False
        customer.unsubscribed_at = None
        customer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def get_customer_segments(db: Session, customer_id: int) -> List[Dict[str, Any]]:
        """Get segments that contain this customer"""
        from app.models.segment import Segment, SegmentCustomer
        
        segment_customers = db.query(SegmentCustomer).filter(
            SegmentCustomer.customer_id == customer_id
        ).all()
        
        segments = []
        for sc in segment_customers:
            segment = db.query(Segment).filter(Segment.id == sc.segment_id).first()
            if segment:
                segments.append({
                    "id": segment.id,
                    "name": segment.name,
                    "description": segment.description,
                })
        
        return segments
    
    @staticmethod
    def get_brand_customer_stats(db: Session, brand_id: int) -> Dict[str, Any]:
        """Get aggregate customer stats for a brand"""
        total = db.query(Customer).filter(Customer.brand_id == brand_id).count()
        
        with_email = db.query(Customer).filter(
            Customer.brand_id == brand_id,
            Customer.email.isnot(None)
        ).count()
        
        with_phone = db.query(Customer).filter(
            Customer.brand_id == brand_id,
            Customer.phone.isnot(None)
        ).count()
        
        unsubscribed = db.query(Customer).filter(
            Customer.brand_id == brand_id,
            Customer.is_unsubscribed == True
        ).count()
        
        # Calculate avg LTV across all customers with orders
        customers_with_orders = db.query(Order.customer_id).filter(
            Order.brand_id == brand_id
        ).distinct().count()
        
        total_revenue = db.query(func.sum(Order.total)).filter(
            Order.brand_id == brand_id
        ).scalar() or 0
        
        avg_ltv = total_revenue / customers_with_orders if customers_with_orders > 0 else 0
        
        return {
            "total_customers": total,
            "customers_with_email": with_email,
            "customers_with_phone": with_phone,
            "unsubscribed_count": unsubscribed,
            "subscribed_count": total - unsubscribed,
            "customers_with_orders": customers_with_orders,
            "total_revenue": float(total_revenue),
            "average_ltv": float(avg_ltv),
        }