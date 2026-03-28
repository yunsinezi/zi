# ============================================================
# Railway Dockerfile - Python Flask 船舶静力学计算系统
# ============================================================

FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ============================================================
# Production stage
# ============================================================
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /app/deps /app/deps

# Copy application code
COPY . .

# Create outputs and uploads directories
RUN mkdir -p outputs uploads

# Set PYTHONPATH to include deps
ENV PYTHONPATH=/app/deps:$PYTHONPATH
ENV MPLBACKEND=Agg
ENV PORT=5000

# Expose port (documentation only)
EXPOSE 5000

# Run the application (shell form to expand $PORT env var)
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
