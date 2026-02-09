# Dockerfile for AI Wealth Companion Backend
# Compatible with HF Spaces (port 7860) and Kubernetes (configurable)

FROM python:3.11-slim

WORKDIR /app

# Install build and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security (HF Spaces requirement)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Port configuration (7860 for HF Spaces, override with PORT env var)
ENV PORT=7860
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application with configurable port
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
