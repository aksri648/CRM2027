import asyncio
import random
from datetime import datetime
from typing import Optional
import httpx


# Channel delivery rates
CHANNEL_DELIVERY_RATES = {
    "whatsapp": 0.92,
    "sms": 0.96,
    "email": 0.87,
    "rcs": 0.85,
}

# Engagement funnel probabilities
P_OPENED_GIVEN_DELIVERED = 0.45
P_READ_GIVEN_OPENED = 0.70
P_CLICKED_GIVEN_READ = 0.30
P_CONVERTED_GIVEN_CLICKED = 0.12


class QueueWorker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.queue = asyncio.Queue()
        self.is_running = False
        self.processed_count = 0

    async def start(self):
        """Start the worker"""
        self.is_running = True
        asyncio.create_task(self._process_queue())
        print(f"Worker {self.worker_id} started")

    async def stop(self):
        """Stop the worker"""
        self.is_running = False
        print(f"Worker {self.worker_id} stopped after processing {self.processed_count} messages")

    async def enqueue(self, job: dict):
        """Add a job to the queue"""
        await self.queue.put(job)

    async def _process_queue(self):
        """Process jobs from the queue"""
        while self.is_running:
            try:
                job = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._process_job(job)
                self.processed_count += 1
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")

    async def _process_job(self, job: dict):
        """Process a single job"""
        communication_id = job.get("communication_id")
        campaign_id = job.get("campaign_id")
        customer_id = job.get("customer_id")
        channel = job.get("channel", "whatsapp")
        message = job.get("message")
        callback_url = job.get("callback_url")
        external_id = job.get("external_id")

        # Wait random delay (1.0 - 4.0 seconds) — simulates network/carrier
        await asyncio.sleep(random.uniform(1.0, 4.0))

        # POST callback with "sent" event immediately
        if callback_url:
            await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "sent", external_id)

        # Determine primary outcome (delivered/failed) using channel weights
        delivery_rate = CHANNEL_DELIVERY_RATES.get(channel, 0.90)
        
        if random.random() < delivery_rate:
            # Delivered
            await asyncio.sleep(random.uniform(1.0, 4.0))
            if callback_url:
                await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "delivered", external_id)

            # Engagement funnel
            if random.random() < P_OPENED_GIVEN_DELIVERED:
                await asyncio.sleep(random.uniform(3.0, 10.0))
                if callback_url:
                    await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "opened", external_id)

                if random.random() < P_READ_GIVEN_OPENED:
                    await asyncio.sleep(random.uniform(2.0, 6.0))
                    if callback_url:
                        await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "read", external_id)

                    if random.random() < P_CLICKED_GIVEN_READ:
                        await asyncio.sleep(random.uniform(1.0, 4.0))
                        if callback_url:
                            await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "clicked", external_id)

                        if random.random() < P_CONVERTED_GIVEN_CLICKED:
                            await asyncio.sleep(random.uniform(2.0, 8.0))
                            if callback_url:
                                await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "converted", external_id)
        else:
            # Failed - use correct delay timing for failed messages
            await asyncio.sleep(random.uniform(2.0, 6.0))
            if callback_url:
                await self._call_callback(callback_url, communication_id, campaign_id, customer_id, channel, "failed", external_id)

    async def _call_callback(
        self,
        url: str,
        communication_id: str,
        campaign_id: str,
        customer_id: str,
        channel: str,
        event: str,
        external_id: str = None,
        retries: int = 3
    ):
        """Call the CRM callback URL with retry logic"""
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json={
                            "communication_id": communication_id,
                            "external_id": external_id,
                            "campaign_id": campaign_id,
                            "customer_id": customer_id,
                            "channel": channel,
                            "event": event,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        headers={"x-api-key": "channel-service-api-key"},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        return True
            except Exception as e:
                print(f"Callback attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    await asyncio.sleep(2 ** (attempt + 1))
        
        print(f"Callback failed after {retries} attempts for {communication_id}")
        return False


async def run_workers(num_workers: int = 3):
    """Run multiple workers"""
    workers = [QueueWorker(f"worker-{i+1}") for i in range(num_workers)]
    
    # Start all workers
    await asyncio.gather(*[w.start() for w in workers])
    
    return workers