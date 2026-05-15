import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/dbname")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SERVICE_NAME = os.getenv("SERVICE_NAME", "fastapi-service")
OTEL_COLLECTOR_URL = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://opentelemetry-collector:4317")
INSTANCE_ID = os.getenv("HOSTNAME", "default-instance")
