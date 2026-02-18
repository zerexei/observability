import asyncio
from fastapi import FastAPI
from metrics import metrics_middleware, metrics_endpoint


app = FastAPI(debug=False)

app.middleware("http")(metrics_middleware)


@app.get("/metrics")
def metrics():
    return metrics_endpoint()


@app.get("/")
async def read_root():
    await asyncio.sleep(0.4)  # Simulate some processing delay
    raise Exception("Simulated error")  # Simulate an error for testing
    return {"Hello": "World"}


@app.get("/alert")
def read_alert():
    return {"message": "alert received"}


@app.get("/health")
def read_health():
    return {"status": "ok"}


# import os
# from opentelemetry import trace
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# # Explicit endpoint prevents weird defaults
# otlp_exporter = OTLPSpanExporter(
#     endpoint=os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "http://opentelemetry-collector:4318/v1/traces")
# )

# resource = Resource(attributes={
#     SERVICE_NAME: "observability-fastapi"
# })

# provider = TracerProvider(resource=resource)
# provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
# trace.set_tracer_provider(provider)

# FastAPIInstrumentor.instrument_app(app)
