# Task: T021 — WebSocket Service Dockerfile
# Multi-stage Python 3.11-slim, non-root user (UID 1001),
# healthcheck on /health port 8003. No DB, no Alembic.

FROM python:3.11-slim AS builder

WORKDIR /build

COPY shared/ /build/shared/
COPY websocket-service/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY websocket-service/app/ /app/app/

USER appuser

EXPOSE 8003

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
