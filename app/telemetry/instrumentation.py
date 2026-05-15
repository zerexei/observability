from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_INSTANCE_ID
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from ..core.config import OTEL_COLLECTOR_URL, SERVICE_NAME as SERVICE_NAME_VAL, INSTANCE_ID
from ..logging.config import setup_logging

def setup_telemetry(app=None, engine=None):
    resource = Resource.create({
        SERVICE_NAME: SERVICE_NAME_VAL,
        SERVICE_INSTANCE_ID: INSTANCE_ID,
    })

    # --- Tracing ---
    tracer_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # --- Instrumentation ---
    if app:
        FastAPIInstrumentor.instrument_app(app)
    
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    
    RedisInstrumentor().instrument()

    setup_logging()

def get_tracer():
    return trace.get_tracer(SERVICE_NAME_VAL)

def get_meter():
    return metrics.get_meter(SERVICE_NAME_VAL)
