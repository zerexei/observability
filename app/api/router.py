import asyncio
import random
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..core.database import get_db, redis_client
from ..telemetry.instrumentation import get_tracer, get_meter

router = APIRouter()
logger = logging.getLogger(__name__)
tracer = get_tracer()
meter = get_meter()

# Custom Metrics
failure_counter = meter.create_counter(
    "app_simulated_failures_total",
    description="Number of simulated failures triggered"
)

@router.get("/")
async def root():
    with tracer.start_as_current_span("root_handler"):
        logger.info("Root endpoint accessed")
        return {"status": "running", "service": "observable-backend"}

@router.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("db_read_operation"):
        logger.info(f"Fetching item {item_id} from DB")
        # Simulate some random DB latency
        if random.random() < 0.2:
            time.sleep(random.uniform(0.1, 0.5))
        
        db.execute(text("SELECT 1")).fetchone()
        return {"item_id": item_id, "db_status": "connected"}

@router.get("/cache/{key}")
async def get_cache(key: str):
    with tracer.start_as_current_span("redis_operation"):
        logger.info(f"Checking cache for {key}")
        val = await redis_client.get(key)
        if not val:
            logger.info(f"Cache miss for {key}")
            await redis_client.set(key, "cached_value", ex=60)
            return {"key": key, "value": "newly_cached", "hit": False}
        return {"key": key, "value": val, "hit": True}

@router.get("/simulate/latency")
async def simulate_latency(ms: Optional[int] = None):
    delay = ms / 1000.0 if ms else random.uniform(0.1, 2.0)
    logger.warning(f"Simulating latency of {delay}s")
    await asyncio.sleep(delay)
    return {"slept_for": delay}

@router.get("/simulate/error")
async def simulate_error():
    if random.random() < 0.7:
        failure_counter.add(1, {"error_type": "simulated_exception"})
        logger.error("A critical simulated error occurred!")
        raise HTTPException(status_code=500, detail="Simulated Backend Failure")
    return {"status": "lucky"}

@router.get("/simulate/heavy-task")
async def heavy_task(background_tasks: BackgroundTasks):
    def process_data():
        with tracer.start_as_current_span("background_processing"):
            logger.info("Starting heavy background task")
            time.sleep(2)
            logger.info("Background task completed")

    background_tasks.add_task(process_data)
    return {"message": "Background task queued"}

@router.get("/health")
def health():
    return {"status": "healthy"}
