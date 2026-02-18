import logging
import os
import time
from fastapi import FastAPI, Request

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as HTTPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def instrument(app: FastAPI):
    resource = Resource.create(
        {
            "service.name": os.getenv("SERVICE_NAME", "observability-fastapi"),
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        }
    )

    # Tracing - Direct to Tempo
    tracer_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(
        endpoint=os.getenv(
            "TEMPO_ENDPOINT",
            "http://tempo:3200/tempo/api/traces",
        )
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # Metrics - Stay with Collector
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
                "http://opentelemetry-collector:4317",
            )
        )
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Logging - Direct to Loki (OTLP HTTP)
    logger_provider = LoggerProvider(resource=resource)
    log_exporter = HTTPLogExporter(
        endpoint=os.getenv(
            "LOKI_ENDPOINT",
            "http://loki:3100/otlp/v1/logs",
        )
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    set_logger_provider(logger_provider)

    # Instrument logging
    logging.basicConfig(level=logging.INFO)
    log_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(log_handler)
    LoggingInstrumentor().instrument(
        set_logging_format=False, tracer_provider=tracer_provider
    )

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
        meter_provider=meter_provider,
        tracer_provider=tracer_provider,
    )

    # Custom Metrics for Alerts
    meter = metrics.get_meter(__name__)
    request_counter = meter.create_counter(
        "app_requests_total",
        description="Total number of requests",
    )
    request_duration = meter.create_histogram(
        "app_request_duration_seconds",
        description="Duration of requests in seconds",
    )

    @app.middleware("http")
    async def record_metrics(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        attributes = {
            "http_status": str(response.status_code),
            "http_method": request.method,
            "http_path": request.url.path,
        }
        request_counter.add(1, attributes)
        request_duration.record(duration, attributes)

        return response
