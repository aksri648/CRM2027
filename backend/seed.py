"""
Seed script for Xeno AI CRM - Simplified
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
import json
from faker import Faker

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import (
    Brand, User, Customer, Segment, Campaign, CampaignStatus, CampaignChannel,
    ABTest, Opportunity, AgentProposal, Settings
)

fake = Faker(['en_IN'])

INDIAN_CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Jaipur']


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created")


def seed_all(db):
    # Brand and user
    existing = db.query(Brand).first()
    if not existing:
        brand = Brand(name="Demo Store", slug="demo-store", email="admin@example.com")
        db.add(brand)
        db.flush()
        
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            brand_id=brand.id
        )
        db.add(user)
        db.commit()
        print("Created brand and user")
    else:
        brand = existing
    
    # Customers
    count = db.query(Customer).count()
    if count == 0:
        customers = []
        for i in range(500):
            c = Customer(
                brand_id=brand.id,
                email=f"user{i}@example.com",
                phone=f"+91{fake.msisdn()[:10]}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                city=random.choice(INDIAN_CITIES),
                gender=random.choice(['male', 'female', 'other']),
                tags='[]'
            )
            customers.append(c)
        db.bulk_save_objects(customers)
        db.commit()
        print(f"Created 500 customers")
    
    # Segments
    count = db.query(Segment).count()
    if count == 0:
        segments = [
            Segment(brand_id=brand.id, name="VIP Customers", description="High-value customers", rules='[{"field":"ltv","op":">","value":10000}]', customer_count=50),
            Segment(brand_id=brand.id, name="Inactive 60+ Days", description="Inactive customers", rules='[{"field":"last_order_days","op":">","value":60}]', customer_count=100),
            Segment(brand_id=brand.id, name="New Customers", description="Recent signups", rules='[{"field":"created_days_ago","op":"<","value":30}]', customer_count=75),
        ]
        for s in segments:
            db.add(s)
        db.commit()
        print("Created segments")
    
    # Campaigns
    count = db.query(Campaign).count()
    if count == 0:
        seg = db.query(Segment).first()
        campaigns = [
            Campaign(brand_id=brand.id, name="Summer Sale", channel=CampaignChannel.WHATSAPP, message_content="Hey {name}! Summer sale!", status=CampaignStatus.SENT, segment_id=seg.id if seg else None),
            Campaign(brand_id=brand.id, name="VIP Reactivation", channel=CampaignChannel.SMS, message_content="We miss you {name}!", status=CampaignStatus.SENT, segment_id=seg.id if seg else None),
            Campaign(brand_id=brand.id, name="New Arrivals", channel=CampaignChannel.EMAIL, message_content="New items {name}!", status=CampaignStatus.SENDING, segment_id=seg.id if seg else None),
        ]
        for c in campaigns:
            db.add(c)
        db.commit()
        print("Created campaigns")
    
    # Opportunities
    count = db.query(Opportunity).count()
    if count == 0:
        opps = [
            Opportunity(title="Cross-sell Accessories", description="Cross-sell to electronics buyers", audience_description="Electronics buyers", expected_revenue=32000, ai_reasoning="23% cross-sell potential"),
            Opportunity(title="At-Risk Reactivation", description="High-value at risk", audience_description="LTV > 2000, last order > 45 days", expected_revenue=45000, ai_reasoning="15-20% conversion expected"),
            Opportunity(title="New Category Exploration", description="Fashion to beauty", audience_description="Fashion buyers", expected_revenue=28000, ai_reasoning="2.3x engagement"),
        ]
        for o in opps:
            db.add(o)
        db.commit()
        print("Created opportunities")
    
    # Proposals
    count = db.query(AgentProposal).count()
    if count == 0:
        seg = db.query(Segment).first()
        props = [
            AgentProposal(title="Summer Sale - VIP", segment_id=seg.id if seg else None, channel="whatsapp", message_template="Hey {name}! Summer sale!", confidence_score=0.87, ai_reasoning="High confidence", status="pending"),
            AgentProposal(title="Reactivation Campaign", segment_id=seg.id if seg else None, channel="sms", message_template="We miss you {name}!", confidence_score=0.72, ai_reasoning="Medium confidence", status="pending"),
        ]
        for p in props:
            db.add(p)
        db.commit()
        print("Created proposals")
    
    # Settings
    count = db.query(Settings).count()
    if count == 0:
        settings = Settings(
            platform_name="Xeno AI Campaign Studio",
            timezone="Asia/Kolkata",
            currency="INR",
            ai_model="GPT-5",
            scan_schedule="Daily at 6:00 AM"
        )
        db.add(settings)
        db.commit()
        print("Created settings")


def main():
    print("=" * 40)
    print("Xeno AI CRM - Seed")
    print("=" * 40)
    
    create_tables()
    db = SessionLocal()
    
    try:
        seed_all(db)
        print("=" * 40)
        print("Seed completed!")
        print("=" * 40)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()