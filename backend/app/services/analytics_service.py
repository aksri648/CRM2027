"""
Analytics Service - Business logic for analytics operations

Per CLAUDE.md responsibilities:
- Dashboard KPIs
- Channel Statistics
- Campaign Statistics
- Funnels
- Revenue Attribution

Analytics Principle:
Never generate fake metrics. Everything from communications and communication_events tables.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from app.models.campaign import Campaign, CampaignStatus
from app.models.communication import Communication, CommunicationStatus, CommunicationEvent, CommunicationEventType
from app.models.customer import Customer
from app.models.order import Order


class AnalyticsService:
    
    @staticmethod
    def get_overview_metrics(db: Session, brand_id: int, period_days: int = 30) -> Dict[str, Any]:
        """
        Get dashboard overview metrics
        
        Per CLAUDE.md:
        Return: { total_customers, active_campaigns, messages_sent, revenue_attributed }
        """
        # Total customers
        total_customers = db.query(Customer).filter(Customer.brand_id == brand_id).count()
        
        # Active campaigns (sending or recently sent)
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        active_campaigns = db.query(Campaign).filter(
            Campaign.brand_id == brand_id,
            Campaign.status.in_([CampaignStatus.SENDING, CampaignStatus.SENT]),
            Campaign.sent_at >= cutoff_date
        ).count()
        
        # Messages sent in period
        messages_sent = db.query(Communication).filter(
            Communication.brand_id == brand_id,
            Communication.sent_at >= cutoff_date,
            Communication.status.in_([
                CommunicationStatus.SENT,
                CommunicationStatus.DELIVERED,
            ])
        ).count()
        
        # Revenue attributed in period (orders from campaigns in period)
        revenue_attributed = db.query(func.sum(Order.total)).join(
            Campaign, Order.campaign_id == Campaign.id
        ).filter(
            Campaign.brand_id == brand_id,
            Order.order_date >= cutoff_date,
            Order.status == "completed"
        ).scalar() or 0
        
        # Calculate trends (compare to previous period)
        prev_cutoff = cutoff_date - timedelta(days=period_days)
        
        prev_customers = db.query(Customer).filter(
            Customer.brand_id == brand_id,
            Customer.created_at >= prev_cutoff,
            Customer.created_at < cutoff_date
        ).count()
        
        prev_messages = db.query(Communication).filter(
            Communication.brand_id == brand_id,
            Communication.sent_at >= prev_cutoff,
            Communication.sent_at < cutoff_date,
            Communication.status.in_([CommunicationStatus.SENT, CommunicationStatus.DELIVERED])
        ).count()
        
        prev_revenue = db.query(func.sum(Order.total)).join(
            Campaign, Order.campaign_id == Campaign.id
        ).filter(
            Campaign.brand_id == brand_id,
            Order.order_date >= prev_cutoff,
            Order.order_date < cutoff_date,
            Order.status == "completed"
        ).scalar() or 0
        
        def calc_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        return {
            "total_customers": total_customers,
            "active_campaigns": active_campaigns,
            "messages_sent": messages_sent,
            "revenue_attributed": float(revenue_attributed),
            "trends": {
                "customers_change": calc_change(total_customers - prev_customers, prev_customers),
                "campaigns_change": active_campaigns,
                "messages_change": calc_change(messages_sent, prev_messages),
                "revenue_change": calc_change(float(revenue_attributed), float(prev_revenue)),
            }
        }
    
    @staticmethod
    def get_channel_stats(db: Session, brand_id: int) -> List[Dict[str, Any]]:
        """
        Get per-channel statistics
        
        Per CLAUDE.md:
        Return: [{ channel, sent, delivery_rate, open_rate, click_rate, conversion_rate }]
        """
        channels = ["whatsapp", "sms", "email", "rcs"]
        stats = []
        
        for channel in channels:
            # Count sent
            sent = db.query(Communication).filter(
                Communication.brand_id == brand_id,
                Communication.channel == channel,
                Communication.status.in_([
                    CommunicationStatus.SENT,
                    CommunicationStatus.DELIVERED,
                    CommunicationStatus.QUEUED
                ])
            ).count()
            
            # Count delivered
            delivered = db.query(Communication).filter(
                Communication.brand_id == brand_id,
                Communication.channel == channel,
                Communication.status == CommunicationStatus.DELIVERED
            ).count()
            
            # Count opened (has opened_at timestamp)
            opened = db.query(Communication).filter(
                Communication.brand_id == brand_id,
                Communication.channel == channel,
                Communication.opened_at.isnot(None)
            ).count()
            
            # Count clicked (has clicked_at timestamp)
            clicked = db.query(Communication).filter(
                Communication.brand_id == brand_id,
                Communication.channel == channel,
                Communication.clicked_at.isnot(None)
            ).count()
            
            # Calculate rates
            delivery_rate = (delivered / sent * 100) if sent > 0 else 0
            open_rate = (opened / delivered * 100) if delivered > 0 else 0
            click_rate = (clicked / delivered * 100) if delivered > 0 else 0
            
            stats.append({
                "channel": channel,
                "sent": sent,
                "delivered": delivered,
                "delivery_rate": round(delivery_rate, 2),
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
            })
        
        return stats
    
    @staticmethod
    def get_campaign_stats(db: Session, campaign_id: int) -> Dict[str, Any]:
        """
        Get detailed campaign statistics
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {}
        
        # Get communication counts
        total = db.query(Communication).filter(
            Communication.campaign_id == campaign_id
        ).count()
        
        sent = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status.in_([CommunicationStatus.SENT, CommunicationStatus.DELIVERED])
        ).count()
        
        delivered = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status == CommunicationStatus.DELIVERED
        ).count()
        
        opened = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.opened_at.isnot(None)
        ).count()
        
        clicked = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.clicked_at.isnot(None)
        ).count()
        
        failed = db.query(Communication).filter(
            Communication.campaign_id == campaign_id,
            Communication.status == CommunicationStatus.FAILED
        ).count()
        
        # Calculate rates
        def rate(part, whole):
            return (part / whole * 100) if whole > 0 else 0
        
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "channel": campaign.channel.value if hasattr(campaign.channel, 'value') else campaign.channel,
            "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
            "sent": sent,
            "delivered": delivered,
            "delivered_rate": round(rate(delivered, sent), 2),
            "opened": opened,
            "opened_rate": round(rate(opened, delivered), 2),
            "clicked": clicked,
            "clicked_rate": round(rate(clicked, delivered), 2),
            "failed": failed,
            "failed_rate": round(rate(failed, sent), 2),
            "revenue": campaign.revenue,
        }
    
    @staticmethod
    def get_funnel_metrics(db: Session, campaign_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get conversion funnel metrics
        
        Per CLAUDE.md:
        Return: { sent, delivered, opened, read, clicked, converted }
        """
        query = db.query(Communication)
        
        if campaign_id:
            query = query.filter(Communication.campaign_id == campaign_id)
        
        # Funnel stages
        sent = query.filter(
            Communication.status.in_([CommunicationStatus.SENT, CommunicationStatus.DELIVERED])
        ).count()
        
        delivered = query.filter(
            Communication.status == CommunicationStatus.DELIVERED
        ).count()
        
        opened = query.filter(
            Communication.opened_at.isnot(None)
        ).count()
        
        # "read" is typically same as opened in many systems
        read = opened
        
        clicked = query.filter(
            Communication.clicked_at.isnot(None)
        ).count()
        
        # Converted = has an attributed order
        if campaign_id:
            converted = db.query(Order).filter(
                Order.campaign_id == campaign_id,
                Order.status == "completed"
            ).count()
        else:
            converted = 0
        
        return {
            "sent": sent,
            "delivered": delivered,
            "opened": opened,
            "read": read,
            "clicked": clicked,
            "converted": converted,
        }
    
    @staticmethod
    def get_revenue_attribution(
        db: Session,
        brand_id: int,
        campaign_id: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get revenue attribution
        
        Per CLAUDE.md: Revenue Attribution
        """
        query = db.query(func.sum(Order.total)).join(
            Campaign, Order.campaign_id == Campaign.id
        ).filter(
            Campaign.brand_id == brand_id,
            Order.status == "completed"
        )
        
        if campaign_id:
            query = query.filter(Order.campaign_id == campaign_id)
        
        total_revenue = query.scalar() or 0
        
        # Calculate by channel
        channel_revenue = {}
        channels = ["whatsapp", "sms", "email", "rcs"]
        
        for channel in channels:
            revenue = db.query(func.sum(Order.total)).join(
                Campaign, Order.campaign_id == Campaign.id
            ).join(
                Communication,
                and_(
                    Communication.campaign_id == Campaign.id,
                    Communication.customer_id == Order.customer_id
                )
            ).filter(
                Campaign.brand_id == brand_id,
                Communication.channel == channel,
                Order.status == "completed"
            ).scalar() or 0
            
            if revenue > 0:
                channel_revenue[channel] = float(revenue)
        
        return {
            "total_revenue": float(total_revenue),
            "by_channel": channel_revenue,
        }
    
    @staticmethod
    def get_customer_journey(
        db: Session,
        customer_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get customer touchpoint journey
        """
        journey = []
        
        # Get communications
        comms = db.query(Communication).filter(
            Communication.customer_id == customer_id
        ).order_by(Communication.sent_at.desc()).limit(limit).all()
        
        for comm in comms:
            journey.append({
                "type": "communication",
                "id": comm.id,
                "date": comm.sent_at.isoformat() if comm.sent_at else None,
                "channel": comm.channel,
                "status": comm.status.value if hasattr(comm.status, 'value') else comm.status,
                "campaign_id": comm.campaign_id,
            })
        
        # Get orders
        orders = db.query(Order).filter(
            Order.customer_id == customer_id
        ).order_by(Order.order_date.desc()).limit(limit).all()
        
        for order in orders:
            journey.append({
                "type": "order",
                "id": order.id,
                "date": order.order_date.isoformat() if order.order_date else None,
                "order_number": order.order_number,
                "total": order.total,
                "campaign_id": order.campaign_id,
            })
        
        # Sort by date
        journey.sort(key=lambda x: x.get("date") or "", reverse=True)
        
        return journey[:limit]
    
    @staticmethod
    def get_trends(
        db: Session,
        brand_id: int,
        metric: str = "revenue",
        period_days: int = 30,
        interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get time-series trends for a metric
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        trends = []
        
        if metric == "revenue":
            # Group orders by day
            for i in range(period_days):
                date = cutoff_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                revenue = db.query(func.sum(Order.total)).filter(
                    Order.brand_id == brand_id,
                    Order.order_date >= date,
                    Order.order_date < next_date,
                    Order.status == "completed"
                ).scalar() or 0
                
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(revenue),
                })
        
        elif metric == "messages":
            for i in range(period_days):
                date = cutoff_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                count = db.query(Communication).filter(
                    Communication.brand_id == brand_id,
                    Communication.sent_at >= date,
                    Communication.sent_at < next_date
                ).count()
                
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": count,
                })
        
        elif metric == "customers":
            for i in range(period_days):
                date = cutoff_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                count = db.query(Customer).filter(
                    Customer.brand_id == brand_id,
                    Customer.created_at >= date,
                    Customer.created_at < next_date
                ).count()
                
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": count,
                })
        
        return trends
    
    @staticmethod
    def get_top_segments(db: Session, brand_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing segments
        """
        from app.models.segment import Segment
        
        segments = db.query(Segment).filter(
            Segment.brand_id == brand_id,
            Segment.is_active == True
        ).all()
        
        segment_performance = []
        
        for segment in segments:
            # Get campaign stats for campaigns targeting this segment
            campaigns = db.query(Campaign).filter(
                Campaign.segment_id == segment.id
            ).all()
            
            total_sent = sum(c.sent_count for c in campaigns)
            total_revenue = sum(c.revenue for c in campaigns)
            
            # Calculate engagement rate
            total_opened = sum(c.opened_count for c in campaigns)
            engagement_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
            
            segment_performance.append({
                "segment_id": segment.id,
                "segment_name": segment.name,
                "customer_count": segment.customer_count,
                "campaign_count": len(campaigns),
                "total_sent": total_sent,
                "total_revenue": float(total_revenue),
                "engagement_rate": round(engagement_rate, 2),
            })
        
        # Sort by engagement rate
        segment_performance.sort(key=lambda x: x["engagement_rate"], reverse=True)
        
        return segment_performance[:limit]
    
    @staticmethod
    def get_engagement_distribution(db: Session, brand_id: int) -> Dict[str, int]:
        """
        Get distribution of customer engagement scores
        """
        customers = db.query(Customer.engagement_score).filter(
            Customer.brand_id == brand_id
        ).all()
        
        distribution = {
            "high": 0,      # > 70
            "medium": 0,    # 40-70
            "low": 0,       # < 40
            "none": 0,      # 0 or null
        }
        
        for (score,) in customers:
            if score is None or score == 0:
                distribution["none"] += 1
            elif score > 70:
                distribution["high"] += 1
            elif score >= 40:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution