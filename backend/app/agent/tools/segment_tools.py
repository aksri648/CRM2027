"""
Segment Tools for Agent

Per CLAUDE.md: Tools for segment operations
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import json

from app.services.segmentation import SegmentationService
from app.models.segment import Segment
from app.schemas.segment import SegmentCreate


class SegmentTools:
    """Tools for segment operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_segment(
        self,
        brand_id: int,
        name: str,
        rules: List[Dict[str, Any]],
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new segment from rules
        """
        rules_json = json.dumps(rules)
        segment_data = SegmentCreate(
            name=name,
            description=description,
            rules=rules_json,
        )
        
        segment = SegmentationService.create_segment(self.db, brand_id, segment_data)
        
        return {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "customer_count": segment.customer_count,
            "rules": rules,
        }
    
    def preview_segment(
        self,
        brand_id: int,
        rules: List[Dict[str, Any]],
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Preview segment without saving
        """
        count, sample = SegmentationService.preview_segment(
            self.db,
            brand_id,
            rules,
            limit=limit
        )
        
        return {
            "customer_count": count,
            "sample_customers": sample,
        }
    
    def get_segment_details(self, segment_id: int) -> Dict[str, Any]:
        """
        Get segment info and customer count
        """
        segment = self.db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return {"error": f"Segment {segment_id} not found"}
        
        rules = json.loads(segment.rules) if segment.rules else []
        
        return {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "customer_count": segment.customer_count,
            "rules": rules,
            "is_active": segment.is_active,
            "created_at": segment.created_at.isoformat() if segment.created_at else None,
        }
    
    def get_segment_stats(self, segment_id: int) -> Dict[str, Any]:
        """
        Get detailed segment statistics
        """
        return SegmentationService.get_segment_stats(self.db, segment_id)
    
    def list_segments(self, brand_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all segments for brand
        """
        segments = self.db.query(Segment).filter(
            Segment.brand_id == brand_id,
            Segment.is_active == True
        ).order_by(Segment.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "customer_count": s.customer_count,
            }
            for s in segments
        ]
    
    def refresh_segment(self, segment_id: int) -> Dict[str, Any]:
        """
        Recalculate segment customer count
        """
        segment = SegmentationService.refresh_segment(self.db, segment_id)
        if not segment:
            return {"error": f"Segment {segment_id} not found"}
        
        return {
            "id": segment.id,
            "name": segment.name,
            "customer_count": segment.customer_count,
        }
    
    def delete_segment(self, segment_id: int) -> bool:
        """
        Delete a segment
        """
        return SegmentationService.delete_segment(self.db, segment_id)