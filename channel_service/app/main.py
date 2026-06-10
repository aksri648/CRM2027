from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncio
import random
import uuid

app = FastAPI(title="Xeno Channel Service", version="1.0.0")

# In-memory storage for communications
communications = {}


class SendRequest(BaseModel):
    external_id: str
    recipient: str
    channel: str  # email, sms, whatsapp, rcs
    subject: Optional[str] = None
    content: str
    callback_url: Optional[str] = None


class SendResponse(BaseModel):
    success: bool
    message: str
    channel_id: str


class StatusResponse(BaseModel):
    external_id: str
    status: str
    channel: str
    recipient: str
    queued_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


def simulate_delivery_outcome(channel_id: str, callback_url: Optional[str]):
    """Simulate the async delivery and engagement flow"""
    async def run_simulation():
        await asyncio.sleep(random.uniform(1, 3))  # 1-3 seconds delay
        
        comm = communications.get(channel_id)
        if not comm:
            return
        
        # Mark as sent
        comm["sent_at"] = datetime.utcnow()
        comm["status"] = "sent"
        
        # Call back if URL provided
        if callback_url:
            await call_callback(callback_url, "sent")
        
        # Simulate delivery (90% success rate)
        await asyncio.sleep(random.uniform(0.5, 2))
        
        if random.random() < 0.9:  # 90% delivered
            comm["delivered_at"] = datetime.utcnow()
            comm["status"] = "delivered"
            if callback_url:
                await call_callback(callback_url, "delivered")
            
            # Simulate open (60% of delivered)
            if random.random() < 0.6:
                await asyncio.sleep(random.uniform(1, 4))
                comm["opened_at"] = datetime.utcnow()
                if callback_url:
                    await call_callback(callback_url, "opened")
                
                # Simulate click (30% of opened)
                if random.random() < 0.3:
                    await asyncio.sleep(random.uniform(0.5, 2))
                    comm["clicked_at"] = datetime.utcnow()
                    if callback_url:
                        await call_callback(callback_url, "clicked")
        else:
            # Failed
            comm["status"] = "failed"
            if callback_url:
                await call_callback(callback_url, "failed")
    
    asyncio.create_task(run_simulation())


async def call_callback(url: str, event_type: str):
    """Call the CRM callback URL"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                json={
                    "event_type": event_type,
                    "metadata": None,
                    "occurred_at": datetime.utcnow().isoformat()
                },
                headers={"x-api-key": "channel-service-api-key"},
                timeout=10.0
            )
    except Exception as e:
        print(f"Callback failed: {e}")


@app.post("/send", response_model=SendResponse)
async def send_message(request: SendRequest, background_tasks: BackgroundTasks):
    """Receive a communication from CRM and simulate delivery"""
    channel_id = str(uuid.uuid4())
    
    communications[channel_id] = {
        "external_id": request.external_id,
        "channel": request.channel,
        "recipient": request.recipient,
        "subject": request.subject,
        "content": request.content,
        "callback_url": request.callback_url,
        "status": "queued",
        "queued_at": datetime.utcnow()
    }
    
    # Start async simulation
    background_tasks.add_task(
        simulate_delivery_outcome, channel_id, request.callback_url
    )
    
    return SendResponse(
        success=True,
        message="Communication queued for delivery",
        channel_id=channel_id
    )


@app.get("/status/{external_id}", response_model=StatusResponse)
async def get_status(external_id: str):
    """Get the status of a communication"""
    for comm in communications.values():
        if comm["external_id"] == external_id:
            return StatusResponse(
                external_id=comm["external_id"],
                status=comm["status"],
                channel=comm["channel"],
                recipient=comm["recipient"],
                queued_at=comm["queued_at"],
                sent_at=comm.get("sent_at"),
                delivered_at=comm.get("delivered_at")
            )
    
    raise HTTPException(status_code=404, detail="Communication not found")


@app.post("/batch-send")
async def batch_send(requests: List[SendRequest], background_tasks: BackgroundTasks):
    """Batch send communications"""
    results = []
    for req in requests:
        channel_id = str(uuid.uuid4())
        communications[channel_id] = {
            "external_id": req.external_id,
            "channel": req.channel,
            "recipient": req.recipient,
            "subject": req.subject,
            "content": req.content,
            "callback_url": req.callback_url,
            "status": "queued",
            "queued_at": datetime.utcnow()
        }
        background_tasks.add_task(
            simulate_delivery_outcome, channel_id, req.callback_url
        )
        results.append({"external_id": req.external_id, "channel_id": channel_id})
    
    return {"results": results, "total": len(results)}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "channel-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)