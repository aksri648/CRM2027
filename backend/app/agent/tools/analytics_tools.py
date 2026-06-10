"""
Analytics Tools for Agent

Per CLAUDE.md: Tools for analytics queries
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService


class AnalyticsTools:
    """Tools for analytics queries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overview(self, brand_id: int, period_days: int = 30) -> Dict[str, Any]:
        """
        Get dashboard overview stats
        """
        return AnalyticsService.get_overview_metrics(self.db, brand_id, period_days)
    
    def get_campaign_performance(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get detailed campaign metrics
        """
        return AnalyticsService.get_campaign_stats(self.db, campaign_id)
    
    def get_channel_performance(self, brand_id: int) -> List[Dict[str, Any]]:
        """
        Get per-channel statistics
        """
        return AnalyticsService.get_channel_stats(self.db, brand_id)
    
    def get_funnel_metrics(self, campaign_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get conversion funnel metrics
        """
        return AnalyticsService.get_funnel_metrics(self.db, campaign_id)
    
    def get_revenue_trends(
        self,
        brand_id: int,
        period_days: int = 30,
        interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get revenue trends over time
        """
        return AnalyticsService.get_trends(
            self.db,
            brand_id,
            metric="revenue",
            period_days=period_days,
            interval=interval
        )
    
    def get_message_trends(
        self,
        brand_id: int,
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get message volume trends
        """
        return AnalyticsService.get_trends(
            self.db,
            brand_id,
            metric="messages",
            period_days=period_days
        )
    
    def get_top_segments(self, brand_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing segments
        """
        return AnalyticsService.get_top_segments(self.db, brand_id, limit)
    
    def get_customer_journey(self, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get customer touchpoint journey
        """
        return AnalyticsService.get_customer_journey(self.db, customer_id, limit)
    
    def get_engagement_distribution(self, brand_id: int) -> Dict[str, int]:
        """
        Get distribution of customer engagement scores
        """
        return AnalyticsService.get_engagement_distribution(self.db, brand_id)
    
    def get_revenue_attribution(
        self,
        brand_id: int,
        campaign_id: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get revenue attribution
        """
        return AnalyticsService.get_revenue_attribution(self.db, brand_id, campaign_id)