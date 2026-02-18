import asyncio
import logging
from fastapi import FastAPI
from instrumentation import instrument


app = FastAPI(debug=False)

instrument(app)

logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    logger.info("Hello from the root endpoint")
    await asyncio.sleep(0.4)  # Simulate some processing delay
    # raise Exception("Simulated error")  # Simulate an error for testing
    return {"Hello": "World"}


@app.get("/alert")
def read_alert():
    return {"message": "alert received"}


@app.get("/health")
def read_health():
    return {"status": "ok"}

