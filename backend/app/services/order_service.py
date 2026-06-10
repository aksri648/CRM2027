"""
Order Service - Business logic for order operations

Per CLAUDE.md responsibilities:
- Order Import
- Order Listing
- Customer Order History
- LTV Recalculation
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    
    @staticmethod
    def create_order(db: Session, brand_id: int, order_data: OrderCreate) -> Order:
        """
        Create a new order with items
        
        Per CLAUDE.md: Order is immutable after creation
        """
        # Generate order number if not provided
        order_number = order_data.order_number
        if not order_number:
            order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order(
            brand_id=brand_id,
            customer_id=order_data.customer_id,
            order_number=order_number,
            status=order_data.status,
            subtotal=order_data.subtotal,
            discount=order_data.discount,
            tax=order_data.tax,
            total=order_data.total,
            channel=order_data.channel,
            source=order_data.source,
            campaign_id=order_data.campaign_id,
            order_date=order_data.order_date or datetime.utcnow(),
        )
        db.add(order)
        db.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_data.items:
            item_total = (item_data.unit_price * item_data.quantity) - item_data.discount
            item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount=item_data.discount,
                total=item_total,
            )
            db.add(item)
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_with_items(db: Session, order_id: int) -> Optional[Order]:
        """Get order with items loaded"""
        return db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(db: Session, brand_id: int, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        return db.query(Order).filter(
            Order.brand_id == brand_id,
            Order.order_number == order_number
        ).first()
    
    @staticmethod
    def get_customer_orders(
        db: Session,
        customer_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Order], int]:
        """
        Get orders for a customer
        
        Returns: (orders, total_count)
        """
        query = db.query(Order).filter(Order.customer_id == customer_id)
        total = query.count()
        orders = query.order_by(Order.order_date.desc()).offset(offset).limit(limit).all()
        return orders, total
    
    @staticmethod
    def list_orders(
        db: Session,
        brand_id: int,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        source: Optional[str] = None,
        campaign_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Order], int]:
        """
        List orders with filters
        
        Returns: (orders, total_count)
        """
        query = db.query(Order).filter(Order.brand_id == brand_id)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if status:
            query = query.filter(Order.status == status)
        if channel:
            query = query.filter(Order.channel == channel)
        if source:
            query = query.filter(Order.source == source)
        if campaign_id:
            query = query.filter(Order.campaign_id == campaign_id)
        if date_from:
            query = query.filter(Order.order_date >= date_from)
        if date_to:
            query = query.filter(Order.order_date <= date_to)
        
        total = query.count()
        orders = query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
        return orders, total
    
    @staticmethod
    def calculate_customer_ltv(db: Session, customer_id: int) -> float:
        """
        Calculate customer Lifetime Value (LTV)
        
        Per CLAUDE.md: ltv computed
        """
        result = db.query(func.sum(Order.total)).filter(
            Order.customer_id == customer_id,
            Order.status == "completed"
        ).scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def recalculate_customer_ltv(db: Session, customer_id: int) -> float:
        """
        Recalculate and return customer LTV
        
        This is useful when orders are added/modified
        """
        return OrderService.calculate_customer_ltv(db, customer_id)
    
    @staticmethod
    def get_recent_orders(db: Session, brand_id: int, days: int = 30) -> List[Order]:
        """Get orders from the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(Order).filter(
            Order.brand_id == brand_id,
            Order.order_date >= cutoff_date
        ).order_by(Order.order_date.desc()).all()
    
    @staticmethod
    def get_order_stats(db: Session, brand_id: int) -> Dict[str, Any]:
        """
        Get aggregate order statistics for a brand
        """
        total_orders = db.query(Order).filter(Order.brand_id == brand_id).count()
        
        completed_orders = db.query(Order).filter(
            Order.brand_id == brand_id,
            Order.status == "completed"
        ).count()
        
        total_revenue = db.query(func.sum(Order.total)).filter(
            Order.brand_id == brand_id,
            Order.status == "completed"
        ).scalar() or 0
        
        avg_order_value = float(total_revenue) / completed_orders if completed_orders > 0 else 0
        
        # Orders by channel
        channel_stats = db.query(
            Order.channel,
            func.count(Order.id).label("count"),
            func.sum(Order.total).label("revenue")
        ).filter(
            Order.brand_id == brand_id,
            Order.status == "completed"
        ).group_by(Order.channel).all()
        
        channels = {}
        for stat in channel_stats:
            channels[stat.channel or "unknown"] = {
                "count": stat.count,
                "revenue": float(stat.revenue) if stat.revenue else 0
            }
        
        # Orders by source
        source_stats = db.query(
            Order.source,
            func.count(Order.id).label("count"),
            func.sum(Order.total).label("revenue")
        ).filter(
            Order.brand_id == brand_id,
            Order.status == "completed"
        ).group_by(Order.source).all()
        
        sources = {}
        for stat in source_stats:
            sources[stat.source or "unknown"] = {
                "count": stat.count,
                "revenue": float(stat.revenue) if stat.revenue else 0
            }
        
        return {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": avg_order_value,
            "by_channel": channels,
            "by_source": sources,
        }
    
    @staticmethod
    def import_orders(db: Session, brand_id: int, orders_data: List[OrderCreate]) -> int:
        """
        Bulk import orders
        
        Returns: count of imported orders
        """
        imported_count = 0
        
        for order_data in orders_data:
            # Check if order already exists
            existing = None
            if order_data.order_number:
                existing = db.query(Order).filter(
                    Order.brand_id == brand_id,
                    Order.order_number == order_data.order_number
                ).first()
            
            if not existing:
                OrderService.create_order(db, brand_id, order_data)
                imported_count += 1
        
        return imported_count
    
    @staticmethod
    def get_customer_order_summary(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Get order summary for a customer
        """
        orders = db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.status == "completed"
        ).all()
        
        if not orders:
            return {
                "total_orders": 0,
                "total_spent": 0,
                "average_order_value": 0,
                "first_order_date": None,
                "last_order_date": None,
            }
        
        total_spent = sum(o.total for o in orders)
        order_dates = [o.order_date for o in orders if o.order_date]
        
        return {
            "total_orders": len(orders),
            "total_spent": total_spent,
            "average_order_value": total_spent / len(orders),
            "first_order_date": min(order_dates) if order_dates else None,
            "last_order_date": max(order_dates) if order_dates else None,
        }
    
    @staticmethod
    def get_orders_by_product(
        db: Session,
        brand_id: int,
        product_id: int,
        limit: int = 100
    ) -> List[Order]:
        """Get orders containing a specific product"""
        order_ids = db.query(OrderItem.order_id).filter(
            OrderItem.product_id == product_id
        ).distinct().subquery()
        
        return db.query(Order).filter(
            Order.brand_id == brand_id,
            Order.id.in_(order_ids)
        ).order_by(Order.order_date.desc()).limit(limit).all()
    
    @staticmethod
    def get_campaign_attributed_orders(
        db: Session,
        campaign_id: int,
        limit: int = 100
    ) -> List[Order]:
        """Get orders attributed to a campaign"""
        return db.query(Order).filter(
            Order.campaign_id == campaign_id
        ).order_by(Order.order_date.desc()).limit(limit).all()
    
    @staticmethod
    def calculate_campaign_revenue(db: Session, campaign_id: int) -> float:
        """Calculate total revenue attributed to a campaign"""
        result = db.query(func.sum(Order.total)).filter(
            Order.campaign_id == campaign_id,
            Order.status == "completed"
        ).scalar()
        return float(result) if result else 0.0