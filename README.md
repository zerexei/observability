# FastAPI Observability Stack

A comprehensive, production-ready observability demonstration featuring a FastAPI application integrated with the full LGTP stack (Loki, Grafana, Tempo, Prometheus) using OpenTelemetry.

## 🚀 Overview

This project showcases how to implement a complete observability lifecycle:
- **Tracing**: Distributed tracing with Tempo.
- **Metrics**: Infrastructure and application metrics with Prometheus.
- **Logging**: Centralized logging with Loki.
- **Alerting**: Proactive monitoring with Alertmanager.
- **Visualization**: Unified dashboards in Grafana.
- **Instrumentation**: Vendor-neutral telemetry via OpenTelemetry.

## 🛠️ Tech Stack

- **Core**: [FastAPI](https://fastapi.tiangolo.com/), [Python 3.12+](https://www.python.org/)
- **Infrastructure**: [Docker Compose](https://docs.docker.com/compose/), [Traefik](https://traefik.io/) (Reverse Proxy)
- **Database & Cache**: [PostgreSQL](https://www.postgresql.org/), [Redis](https://redis.io/)
- **Storage**: [MinIO](https://min.io/) (S3-compatible storage for Loki/Tempo)
- **Observability**:
  - [OpenTelemetry](https://opentelemetry.io/) (SDKs & Collector)
  - [Prometheus](https://prometheus.io/) (Metrics)
  - [Grafana Loki](https://grafana.com/oss/loki/) (Logs)
  - [Grafana Tempo](https://grafana.com/oss/tempo/) (Traces)
  - [Grafana](https://grafana.com/) (Dashboards)
  - [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) (Alerting)

## 🏗️ Architecture

The system is composed of multiple microservices orchestrated by Docker Compose:

- **Server**: 5 replicas of the FastAPI application, load-balanced by Traefik.
- **Telemetry Flow**:
    - **Traces**: Sent directly to Tempo via OTLP/gRPC.
    - **Metrics**: Sent to OpenTelemetry Collector, then scraped by Prometheus.
    - **Logs**: Sent directly to Loki via OTLP/HTTP.
- **Exporters**: Dedicated exporters for PostgreSQL and Redis to provide deep infrastructure insights.

## 🚦 Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js (optional, for load testing with k6)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd observability
   ```

2. **Configure Environment**:
   Copy the example environment file and adjust values if necessary:
   ```bash
   cp .env.example .env
   ```

3. **Launch the Stack**:
   ```bash
   docker compose up -d
   ```

### Accessing the Services

The project uses Traefik to provide clean local hostnames (ensure your `hosts` file points these to `127.0.0.1` or use a tool like `dnsmasq`):

| Service | URL | Description |
| :--- | :--- | :--- |
| **FastAPI App** | [http://server.localhost](http://server.localhost) | The main application API |
| **Grafana** | [http://grafana.localhost](http://grafana.localhost) | Visualization & Dashboards |
| **Prometheus** | [http://prometheus.localhost](http://prometheus.localhost) | Metrics exploration |
| **Alertmanager** | [http://alertmanager.localhost](http://alertmanager.localhost) | Alert management |
| **MinIO Console**| [http://minio.localhost](http://minio.localhost) | Object storage UI |
| **Traefik Dashboard** | [http://localhost:8080](http://localhost:8080) | Proxy & Load Balancer status |

## 🧪 Load Testing

To see the observability stack in action, generate some traffic using the provided [k6](https://k6.io/) script:

```bash
# Using local k6 installation
k6 run scripts/load-test.js
```

The load test simulates concurrent users hitting various endpoints, which will populate Grafana dashboards with real-time metrics, traces, and logs.

## 📊 Observability Features

- **Correlation**: Logs are automatically enriched with `trace_id` and `span_id`, allowing seamless navigation from a log entry to its corresponding trace in Grafana.
- **Custom Metrics**: The application tracks `app_requests_total` and `app_request_duration_seconds` with high-cardinality attributes like HTTP status and path.
- **Infrastructure Monitoring**: Built-in dashboards for hardware (Node Exporter), Database (Postgres Exporter), and Cache (Redis Exporter).

## 🚨 Alerting & Monitoring

The project includes pre-configured alerting rules in Prometheus to monitor the application's health:

- **HighErrorRate**: Triggered if the rate of `5xx` responses exceeds 1/sec for 30s.
- **HighLatency**: Triggered if the P95 latency is above 1 second for 1 minute.
- **PostgresDown**: Immediate alert if the database becomes unreachable.

Alerts are routed via **Alertmanager**, which can be accessed at `http://alertmanager.localhost`.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
