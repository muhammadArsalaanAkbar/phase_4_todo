# Task: T017 — Todo Service Dockerfile
# Multi-stage Python 3.11-slim, non-root user (UID 1001),
# healthcheck on /health port 8001, install shared lib

FROM python:3.11-slim AS builder

WORKDIR /build

# Copy shared library first (dependency)
COPY shared/ /build/shared/

# Copy service requirements and install
COPY todo-service/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.11-slim

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY todo-service/app/ /app/app/
COPY todo-service/alembic/ /app/alembic/
COPY todo-service/alembic.ini /app/alembic.ini

# Switch to non-root user
USER appuser

EXPOSE 8001

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
