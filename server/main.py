from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()

# Initialize the Instrumentator for Prometheus metrics
instrumentator = Instrumentator()

# Instrument your FastAPI app to expose /metrics
instrumentator.instrument(app).expose(app)


@app.get("/")
def read_root():
    print("hello")
    return {"Hello": "World"}


@app.get("/health")
def read_health():
    return {"status": "ok"}