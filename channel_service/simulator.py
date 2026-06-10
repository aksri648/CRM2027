import asyncio
import random
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class DeliveryOutcome:
    communication_id: str
    channel: str
    sent: bool = False
    delivered: bool = False
    failed: bool = False
    opened: bool = False
    read: bool = False
    clicked: bool = False
    converted: bool = False
    events: List[Dict] = field(default_factory=list)


class ChannelSimulator:
    """Simulates channel delivery and engagement"""
    
    # Channel delivery rates
    CHANNEL_DELIVERY_RATES = {
        "whatsapp": 0.92,
        "sms": 0.96,
        "email": 0.87,
        "rcs": 0.85,
    }
    
    # Engagement funnel (conditional probabilities)
    P_OPENED_GIVEN_DELIVERED = 0.45
    P_READ_GIVEN_OPENED = 0.70
    P_CLICKED_GIVEN_READ = 0.30
    P_CONVERTED_GIVEN_CLICKED = 0.12
    
    # Event delays (in seconds)
    DELAYS = {
        "sent": (1.0, 4.0),
        "delivered": (1.0, 4.0),
        "opened": (3.0, 10.0),
        "read": (2.0, 6.0),
        "clicked": (1.0, 4.0),
        "converted": (2.0, 8.0),
    }
    
    def __init__(self):
        self.outcomes: Dict[str, DeliveryOutcome] = {}
        self.stats = {
            "total_sent": 0,
            "outcomes": {
                "delivered": 0,
                "failed": 0,
                "opened": 0,
                "read": 0,
                "clicked": 0,
                "converted": 0,
            }
        }
    
    async def simulate(self, communication_id: str, channel: str) -> DeliveryOutcome:
        """Simulate delivery for a single communication"""
        outcome = DeliveryOutcome(communication_id=communication_id, channel=channel)
        self.outcomes[communication_id] = outcome
        
        # Sent event
        await self._wait_random("sent")
        outcome.sent = True
        outcome.events.append({
            "event": "sent",
            "timestamp": datetime.utcnow().isoformat()
        })
        self.stats["total_sent"] += 1
        
        # Determine if delivered or failed
        delivery_rate = self.CHANNEL_DELIVERY_RATES.get(channel, 0.90)
        
        if random.random() < delivery_rate:
            # Delivered
            await self._wait_random("delivered")
            outcome.delivered = True
            outcome.events.append({
                "event": "delivered",
                "timestamp": datetime.utcnow().isoformat()
            })
            self.stats["outcomes"]["delivered"] += 1
            
            # Engagement funnel
            if random.random() < self.P_OPENED_GIVEN_DELIVERED:
                await self._wait_random("opened")
                outcome.opened = True
                outcome.events.append({
                    "event": "opened",
                    "timestamp": datetime.utcnow().isoformat()
                })
                self.stats["outcomes"]["opened"] += 1
                
                if random.random() < self.P_READ_GIVEN_OPENED:
                    await self._wait_random("read")
                    outcome.read = True
                    outcome.events.append({
                        "event": "read",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    self.stats["outcomes"]["read"] += 1
                    
                    if random.random() < self.P_CLICKED_GIVEN_READ:
                        await self._wait_random("clicked")
                        outcome.clicked = True
                        outcome.events.append({
                            "event": "clicked",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        self.stats["outcomes"]["clicked"] += 1
                        
                        if random.random() < self.P_CONVERTED_GIVEN_CLICKED:
                            await self._wait_random("converted")
                            outcome.converted = True
                            outcome.events.append({
                                "event": "converted",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            self.stats["outcomes"]["converted"] += 1
        else:
            # Failed
            await self._wait_random("delivered")
            outcome.failed = True
            outcome.events.append({
                "event": "failed",
                "timestamp": datetime.utcnow().isoformat()
            })
            self.stats["outcomes"]["failed"] += 1
        
        return outcome
    
    async def _wait_random(self, event: str):
        """Wait a random amount of time for an event"""
        min_delay, max_delay = self.DELAYS.get(event, (1.0, 4.0))
        await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            "total_sent": self.stats["total_sent"],
            "outcomes": self.stats["outcomes"].copy()
        }
    
    def get_outcome(self, communication_id: str) -> DeliveryOutcome:
        """Get outcome for a specific communication"""
        return self.outcomes.get(communication_id)


# Global simulator instance
simulator = ChannelSimulator()