import logging
from fastapi import FastAPI
from .core.database import engine, init_db
from .telemetry.instrumentation import setup_telemetry
from .api.router import router

# Initialize App
app = FastAPI(title="Observability-Driven Platform")

# Setup Telemetry & DB
init_db()
setup_telemetry(app, engine)

# Include Routes
app.include_router(router)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Observable service started successfully")
