import time
import os
from typing import Callable, Awaitable

from fastapi import Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

INSTANCE_NAME = os.getenv("HOSTNAME", "unknown")

# =========================
# Application Metrics
# =========================

HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code", "instance"],
)

HTTP_REQUEST_EXCEPTIONS_TOTAL = Counter(
    "app_http_request_exceptions_total",
    "Total unhandled exceptions",
    ["method", "route", "instance"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "route", "instance"],
    # SLO-aligned buckets
    buckets=(0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "app_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["instance"],
)


# =========================
# Middleware
# =========================


async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:

    # Skip metrics endpoint itself
    if request.url.path == "/metrics":
        return await call_next(request)

    route = request.scope.get("route")
    route_path = route.path if route else "unknown"

    HTTP_REQUESTS_IN_PROGRESS.labels(instance=INSTANCE_NAME).inc()

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    except Exception:
        HTTP_REQUEST_EXCEPTIONS_TOTAL.labels(
            method=request.method,
            route=route_path,
            instance=INSTANCE_NAME,
        ).inc()
        raise

    finally:
        duration = time.perf_counter() - start_time

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            route=route_path,
            instance=INSTANCE_NAME,
        ).observe(duration)

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            route=route_path,
            status_code=status_code,
            instance=INSTANCE_NAME,
        ).inc()

        HTTP_REQUESTS_IN_PROGRESS.labels(instance=INSTANCE_NAME).dec()


# =========================
# /metrics endpoint
# =========================


def metrics_endpoint() -> Response:
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
