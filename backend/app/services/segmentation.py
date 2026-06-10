"""
Segmentation Service - Business logic for segment operations

Per CLAUDE.md responsibilities:
- Convert filter rules into SQLAlchemy queries
- Preview Segments
- Count Customers
- Return Sample Customers
- Save Segments

Supported operators: >, <, =, contains, in, between
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json

from app.models.segment import Segment
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.segment import SegmentCreate, SegmentUpdate


class SegmentationService:
    
    @staticmethod
    def evaluate_rules(db: Session, brand_id: int, rules: List[Dict]) -> List[Customer]:
        """
        Apply segment rules to filter customers
        
        Per CLAUDE.md: Convert filter rules into SQLAlchemy queries
        """
        query = db.query(Customer).filter(Customer.brand_id == brand_id)
        
        for rule in rules:
            field = rule.get("field")
            operator = rule.get("operator")
            value = rule.get("value")
            
            query = SegmentationService._apply_rule(db, query, brand_id, field, operator, value)
        
        return query.all()
    
    @staticmethod
    def _apply_rule(db: Session, query, brand_id: int, field: str, operator: str, value: Any):
        """Apply a single rule to the query"""
        
        # Order-based fields require subqueries
        order_fields = ["total_orders", "total_spent", "average_order_value", "days_since_last_order"]
        
        if field in order_fields:
            return SegmentationService._apply_order_rule(db, query, brand_id, field, operator, value)
        
        # Customer-based fields
        return SegmentationService._apply_customer_rule(query, field, operator, value)
    
    @staticmethod
    def _apply_order_rule(db: Session, query, brand_id: int, field: str, operator: str, value: Any):
        """Apply order-based rule using subquery"""
        
        if field == "total_orders":
            subq = db.query(
                Order.customer_id,
                func.count(Order.id).label("total_orders")
            ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
            query = query.outerjoin(subq, Customer.id == subq.c.customer_id)
            
            if operator == "greater_than":
                return query.filter(subq.c.total_orders > int(value))
            elif operator == "less_than":
                return query.filter(subq.c.total_orders < int(value))
            elif operator == "equals":
                return query.filter(subq.c.total_orders == int(value))
        
        elif field == "total_spent":
            subq = db.query(
                Order.customer_id,
                func.sum(Order.total).label("total_spent")
            ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
            query = query.outerjoin(subq, Customer.id == subq.c.customer_id)
            
            if operator == "greater_than":
                return query.filter(subq.c.total_spent > float(value))
            elif operator == "less_than":
                return query.filter(subq.c.total_spent < float(value))
            elif operator == "equals":
                return query.filter(subq.c.total_spent == float(value))
        
        elif field == "average_order_value":
            subq = db.query(
                Order.customer_id,
                (func.sum(Order.total) / func.count(Order.id)).label("avg_order_value")
            ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
            query = query.outerjoin(subq, Customer.id == subq.c.customer_id)
            
            if operator == "greater_than":
                return query.filter(subq.c.avg_order_value > float(value))
            elif operator == "less_than":
                return query.filter(subq.c.avg_order_value < float(value))
        
        elif field == "days_since_last_order":
            days = int(value)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            subq = db.query(
                Order.customer_id,
                func.max(Order.order_date).label("last_order")
            ).filter(Order.brand_id == brand_id).group_by(Order.customer_id).subquery()
            query = query.outerjoin(subq, Customer.id == subq.c.customer_id)
            
            if operator == "greater_than":
                return query.filter(
                    (subq.c.last_order < cutoff_date) | 
                    (subq.c.last_order.is_(None))
                )
            elif operator == "less_than":
                return query.filter(subq.c.last_order >= cutoff_date)
        
        return query
    
    @staticmethod
    def _apply_customer_rule(query, field: str, operator: str, value: Any):
        """Apply customer-based rule directly"""
        
        if field == "email":
            if operator == "is_null":
                return query.filter(Customer.email.is_(None))
            elif operator == "is_not_null":
                return query.filter(Customer.email.isnot(None))
            elif operator == "contains":
                return query.filter(Customer.email.ilike(f"%{value}%"))
            elif operator == "equals":
                return query.filter(Customer.email == value)
        
        elif field == "phone":
            if operator == "is_null":
                return query.filter(Customer.phone.is_(None))
            elif operator == "is_not_null":
                return query.filter(Customer.phone.isnot(None))
            elif operator == "contains":
                return query.filter(Customer.phone.ilike(f"%{value}%"))
        
        elif field == "city":
            if operator == "contains":
                return query.filter(Customer.city.ilike(f"%{value}%"))
            elif operator == "equals":
                return query.filter(Customer.city == value)
        
        elif field == "state":
            if operator == "contains":
                return query.filter(Customer.state.ilike(f"%{value}%"))
            elif operator == "equals":
                return query.filter(Customer.state == value)
        
        elif field == "country":
            if operator == "equals":
                return query.filter(Customer.country == value)
        
        elif field == "gender":
            if operator == "equals":
                return query.filter(Customer.gender == value)
        
        elif field == "is_unsubscribed":
            bool_val = value.lower() == "true" if isinstance(value, str) else bool(value)
            return query.filter(Customer.is_unsubscribed == bool_val)
        
        elif field == "engagement_score":
            if operator == "greater_than":
                return query.filter(Customer.engagement_score > int(value))
            elif operator == "less_than":
                return query.filter(Customer.engagement_score < int(value))
            elif operator == "equals":
                return query.filter(Customer.engagement_score == int(value))
        
        elif field == "tags":
            if operator == "contains":
                return query.filter(Customer.tags.ilike(f"%{value}%"))
            elif operator == "equals":
                return query.filter(Customer.tags == value)
        
        return query
    
    @staticmethod
    def preview_segment(
        db: Session,
        brand_id: int,
        rules: List[Dict],
        limit: int = 10
    ) -> Tuple[int, List[Dict]]:
        """
        Preview segment without saving
        
        Per CLAUDE.md: Preview Segments, Return Sample Customers
        
        Returns: (customer_count, sample_customers)
        """
        customers = SegmentationService.evaluate_rules(db, brand_id, rules)
        count = len(customers)
        
        # Get sample customers
        sample = customers[:limit]
        sample_data = [
            {
                "id": c.id,
                "email": c.email,
                "phone": c.phone,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "city": c.city,
            }
            for c in sample
        ]
        
        return count, sample_data
    
    @staticmethod
    def count_segment_customers(db: Session, brand_id: int, rules: List[Dict]) -> int:
        """
        Count customers matching rules
        
        Per CLAUDE.md: Count Customers
        """
        customers = SegmentationService.evaluate_rules(db, brand_id, rules)
        return len(customers)
    
    @staticmethod
    def evaluate_segment(db: Session, segment_id: int) -> List[Customer]:
        """
        Get all customers in a segment
        
        Per CLAUDE.md: Save Segments (evaluation)
        """
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return []
        
        rules = json.loads(segment.rules)
        return SegmentationService.evaluate_rules(db, segment.brand_id, rules)
    
    @staticmethod
    def create_segment(
        db: Session,
        brand_id: int,
        segment_data: SegmentCreate
    ) -> Segment:
        """
        Create a new segment with customer count
        
        Per CLAUDE.md: Save Segments
        """
        segment = Segment(
            brand_id=brand_id,
            name=segment_data.name,
            description=segment_data.description,
            rules=segment_data.rules,
            is_active=segment_data.is_active,
        )
        db.add(segment)
        db.flush()
        
        # Calculate customer count
        rules = json.loads(segment_data.rules)
        segment.customer_count = SegmentationService.count_segment_customers(db, brand_id, rules)
        
        db.commit()
        db.refresh(segment)
        return segment
    
    @staticmethod
    def update_segment(
        db: Session,
        segment_id: int,
        segment_data: SegmentUpdate
    ) -> Optional[Segment]:
        """Update a segment and recalculate customer count"""
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return None
        
        update_data = segment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(segment, field, value)
        
        # Recalculate customer count if rules changed
        if segment_data.rules is not None:
            rules = json.loads(segment_data.rules)
            segment.customer_count = SegmentationService.count_segment_customers(
                db, segment.brand_id, rules
            )
        
        segment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(segment)
        return segment
    
    @staticmethod
    def delete_segment(db: Session, segment_id: int) -> bool:
        """Delete a segment"""
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return False
        
        db.delete(segment)
        db.commit()
        return True
    
    @staticmethod
    def refresh_segment(db: Session, segment_id: int) -> Optional[Segment]:
        """
        Recalculate customer count for a segment
        """
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return None
        
        rules = json.loads(segment.rules)
        segment.customer_count = SegmentationService.count_segment_customers(
            db, segment.brand_id, rules
        )
        segment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(segment)
        return segment
    
    @staticmethod
    def refresh_all_segments(db: Session, brand_id: int) -> int:
        """
        Refresh customer counts for all segments
        
        Per CLAUDE.md: Refresh Dynamic Segments
        
        Returns: number of segments refreshed
        """
        segments = db.query(Segment).filter(Segment.brand_id == brand_id).all()
        refreshed = 0
        
        for segment in segments:
            rules = json.loads(segment.rules)
            segment.customer_count = SegmentationService.count_segment_customers(
                db, brand_id, rules
            )
            segment.updated_at = datetime.utcnow()
            refreshed += 1
        
        db.commit()
        return refreshed
    
    @staticmethod
    def get_segment_stats(db: Session, segment_id: int) -> Dict[str, Any]:
        """
        Get detailed segment statistics
        
        Per CLAUDE.md: Count Customers (extended stats)
        """
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return {}
        
        customers = SegmentationService.evaluate_segment(db, segment_id)
        
        # Calculate demographic breakdown
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
            "segment_id": segment_id,
            "segment_name": segment.name,
            "total_customers": len(customers),
            "customers_with_email": total_with_email,
            "customers_with_phone": total_with_phone,
            "top_cities": sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10],
            "gender_breakdown": genders,
        }
    
    @staticmethod
    def get_segment_customers_paginated(
        db: Session,
        segment_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Customer], int]:
        """
        Get segment customers with pagination
        
        Returns: (customers, total_count)
        """
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return [], 0
        
        rules = json.loads(segment.rules)
        all_customers = SegmentationService.evaluate_rules(db, segment.brand_id, rules)
        total = len(all_customers)
        
        return all_customers[skip:skip + limit], total