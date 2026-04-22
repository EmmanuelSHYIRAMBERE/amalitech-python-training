# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-alpine AS builder
WORKDIR /app

# Build dependencies for psycopg2 on Alpine
RUN apk add --no-cache gcc musl-dev libpq-dev

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-alpine
WORKDIR /app

# Runtime dependency for psycopg2
RUN apk add --no-cache libpq

COPY --from=builder /install /usr/local
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Run as non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
