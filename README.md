# Observability-Driven Backend Platform (FastAPI + OpenTelemetry Stack)

## Overview

This project is a backend system designed to evaluate observability as a first-class engineering concern in distributed applications. It demonstrates how a production-style FastAPI service behaves under load, failure, and concurrency pressure while being fully instrumented for logs, metrics, and traces.

The focus is not feature delivery, but system-level behavior: how requests propagate, how failures surface, and how quickly the system can be debugged using observability signals.

Key goals:

- End-to-end request visibility across services
- Observable async and concurrent request execution
- Failure detection and debugging through telemetry
- Production-style operational insight under load

## Architecture
```
The system is designed as a distributed backend with explicit instrumentation at every execution layer.

Client / Load Generator (k6)
        │
        ▼
Load Balanced FastAPI Service (Traefik, 5 replicas)
        │
        ▼
Application Layer (business workflows)
        │
        ▼
Instrumentation Layer (OpenTelemetry SDK)
        │
 ┌──────────────┬──────────────┬──────────────┐
 ▼              ▼              ▼
Logs (Loki)   Metrics (Prometheus)   Traces (Tempo)
        │              │               │
        └──────────────┴──────────────┘
                       ▼
                 Grafana (Correlation + Dashboards)
```

## Core Components
- API Layer: FastAPI service handling concurrent HTTP requests
- Worker/Processing Layer: Async execution paths simulating real backend workflows
- Telemetry Pipeline: OpenTelemetry Collector exporting to Prometheus, Loki, and Tempo
- Data Stores: PostgreSQL (state), Redis (cache + coordination)
- Load Balancer: Traefik routing traffic across service replicas
- Observability Stack: Grafana for unified visualization and correlation

## Key Features
Distributed Request Visibility
- Each request is assigned a correlation context (trace_id/span_id)
- Full lifecycle tracking across API → service logic → external dependencies
High-Concurrency API Layer
- Multi-replica FastAPI deployment behind a load balancer
- Concurrent request handling with async I/O
- Designed to expose race conditions and bottlenecks under load
Event-Driven Observability Model
- Logs, metrics, and traces emitted at each execution boundary
- Structured telemetry enables cross-signal debugging (log ↔ trace ↔ metric correlation)
Failure Simulation Layer
- Injected latency spikes
- Controlled exception bursts
- Retry storms with backoff behavior
- Queue/backpressure simulation for throughput stress testing

## Async Processing Model

The system is designed around non-blocking request execution and event-driven workflows.

Execution Flow
1. Client request enters FastAPI async endpoint
2. Request context is propagated across async service layers
3. Background tasks simulate downstream work (DB/cache/external calls)
4. Telemetry emitted at each step (metrics + spans + logs)
5. Response returned without blocking global execution pipeline

Concurrency Characteristics
- Async I/O for all I/O-bound operations
- Controlled concurrency boundaries for downstream dependencies
- Safe execution under concurrent load bursts
- Designed to expose contention points (DB, cache, external calls)

Queue/Backpressure Simulation

While not a full message queue system, the architecture simulates:

- Worker saturation under high throughput
- Delayed task execution under load
- Backpressure effects on upstream request latency

## Reliability Design
Fault Tolerance Patterns
- Retry Strategy
  - Exponential backoff on transient failures
  - Retry limits to prevent cascading failures
- Failure Isolation
  - Fault injection is scoped per service layer
  - Failures do not immediately propagate globally
- Graceful Degradation
  - Cache fallback paths (Redis)
  - Reduced dependency coupling in critical request paths
Observability-Driven Debugging
- Full request trace reconstruction via Tempo
- Centralized log aggregation via Loki
- Metrics-based anomaly detection (Prometheus)
Load & Stress Validation
- k6-based load testing simulating concurrent users
- Observability validation under:
  - High RPS conditions
  - Elevated error rates
  - Latency degradation scenarios
Key SLO Signals
- Request latency (p50 / p95 / p99)
- Error rate per endpoint
- Throughput (requests per second)
- Dependency health (DB/Redis saturation)

## Tech Stack
Backend
- FastAPI
- Python 3.12+
Infrastructure
- Docker Compose
- Traefik (reverse proxy / load balancing)
- PostgreSQL (state persistence)
- Redis (cache + coordination layer)
- MinIO (object storage for observability backends)
Observability
- OpenTelemetry (instrumentation + collector)
- Prometheus (metrics)
- Loki (logs)
- Tempo (distributed tracing)
- Grafana (visualization + correlation)
- Alertmanager (alert routing)
Load Testing
- k6 (concurrent traffic simulation)

## Running Locally
Prerequisites
- Docker + Docker Compose
- (Optional) k6 for load testing

Setup
```
git clone <repository-url>
cd observability
cp .env.example .env
docker compose up -d
```

Service Access

| Service           | URL                                                            |
| ----------------- | -------------------------------------------------------------- |
| FastAPI Service   | [http://server.localhost](http://server.localhost)             |
| Grafana           | [http://grafana.localhost](http://grafana.localhost)           |
| Prometheus        | [http://prometheus.localhost](http://prometheus.localhost)     |
| Alertmanager      | [http://alertmanager.localhost](http://alertmanager.localhost) |
| MinIO Console     | [http://minio.localhost](http://minio.localhost)               |
| Traefik Dashboard | [http://localhost:8080](http://localhost:8080)                 |

Load Testing
```
k6 run scripts/load-test.js
```
This generates concurrent traffic to validate:

- tracing propagation
- metric accuracy under load
- log correlation consistency
- system behavior under stress

## Engineering Tradeoffs
- Microservice-style observability stack vs simplicity
  - Chosen to reflect production-like debugging workflows rather than minimal setup
- Full telemetry everywhere vs performance overhead
  - Acceptable overhead to prioritize observability correctness
- Simulated queues vs real message broker
  - Keeps system focused on observability rather than infrastructure complexity
- Stateless API replicas
  - Enables horizontal scaling and exposes concurrency issues clearly under load

## Key Takeaways

This system demonstrates how backend services behave when treated as observable, concurrent, failure-prone distributed systems. It focuses on:

- Production-style instrumentation boundaries
- Async execution under real concurrency pressure
- Failure visibility and debugging workflows
- Cross-signal correlation (logs, metrics, traces)
- System behavior under controlled degradation scenarios
