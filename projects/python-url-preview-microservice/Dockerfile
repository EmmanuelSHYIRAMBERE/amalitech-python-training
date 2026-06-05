# ---------------------------------------------------------------------------
# Stage 1: builder — compile C extensions + install Python packages
# ---------------------------------------------------------------------------
FROM python:3.11-alpine AS builder

RUN apk add --no-cache gcc musl-dev libpq-dev

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------------------------------------------------------------------------
# Stage 2: runtime — minimal image
# ---------------------------------------------------------------------------
FROM python:3.11-alpine

RUN apk add --no-cache libpq curl

COPY --from=builder /install /usr/local

# Non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
