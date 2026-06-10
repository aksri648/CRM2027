"""
Customer Tools for Agent

Per CLAUDE.md: Tools for customer data access
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.services.customer_service import CustomerService
from app.models.customer import Customer


class CustomerTools:
    """Tools for accessing and manipulating customer data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_customer_summary(self, brand_id: int, customer_id: int) -> Dict[str, Any]:
        """
        Get customer overview with stats
        """
        customer = CustomerService.get_customer(self.db, customer_id)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        stats = CustomerService.get_customer_stats(self.db, customer_id)
        
        return {
            "id": customer.id,
            "email": customer.email,
            "phone": customer.phone,
            "name": f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
            "city": customer.city,
            "engagement_score": customer.engagement_score,
            "is_unsubscribed": customer.is_unsubscribed,
            "total_orders": stats.get("total_orders", 0),
            "total_spent": stats.get("total_spent", 0),
            "average_order_value": stats.get("average_order_value", 0),
            "days_since_last_order": stats.get("days_since_last_order"),
        }
    
    def list_customers(
        self,
        brand_id: int,
        query: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search and list customers
        """
        customers, total = CustomerService.search_customers(
            self.db,
            brand_id=brand_id,
            query=query,
            limit=limit
        )
        
        return [
            {
                "id": c.id,
                "email": c.email,
                "phone": c.phone,
                "name": f"{c.first_name or ''} {c.last_name or ''}".strip(),
                "city": c.city,
                "engagement_score": c.engagement_score,
            }
            for c in customers
        ]
    
    def get_customer_segments(self, brand_id: int, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get segment membership for a customer
        """
        return CustomerService.get_customer_segments(self.db, customer_id)
    
    def get_customer_orders(self, brand_id: int, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get order history for a customer
        """
        from app.services.order_service import OrderService
        
        orders, _ = OrderService.get_customer_orders(self.db, customer_id, limit=limit)
        
        return [
            {
                "id": o.id,
                "order_number": o.order_number,
                "total": o.total,
                "status": o.status,
                "order_date": o.order_date.isoformat() if o.order_date else None,
            }
            for o in orders
        ]
    
    def get_customer_timeline(self, brand_id: int, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get customer activity timeline
        """
        return CustomerService.get_customer_timeline(self.db, customer_id, limit=limit)
    
    def get_brand_customer_stats(self, brand_id: int) -> Dict[str, Any]:
        """
        Get aggregate customer stats for brand
        """
        return CustomerService.get_brand_customer_stats(self.db, brand_id)
    
    def get_customer_distribution(self, brand_id: int) -> Dict[str, Any]:
        """
        Get customer demographic distribution
        """
        customers = self.db.query(Customer).filter(Customer.brand_id == brand_id).all()
        
        cities = {}
        genders = {}
        total_with_email = 0
        total_with_phone = 0
        
        for customer in customers:
            if customer.city:
                cities[customer.city] = cities.get(customer.city, 0) + 1
            if customer.gender:
                genders[customer.gender] = genders.get(customer.gender, 0) + 1
            if customer.email:
                total_with_email += 1
            if customer.phone:
                total_with_phone += 1
        
        return {
            "total_customers": len(customers),
            "customers_with_email": total_with_email,
            "customers_with_phone": total_with_phone,
            "top_cities": sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10],
            "gender_distribution": genders,
        }