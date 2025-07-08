# Multi-stage build for Tileshop RAG production deployment
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages and web scraping
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libc6-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash tileshop

# Set working directory
WORKDIR /app

# Copy installed packages from base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Create directories with proper permissions
RUN mkdir -p /app/storage /app/logs /app/temp /app/instance && \
    chown -R tileshop:tileshop /app

# Copy application code
COPY --chown=tileshop:tileshop . .

# Copy production configuration files
COPY --chown=tileshop:tileshop gunicorn.conf.py ./
COPY --chown=tileshop:tileshop health_check.py ./

# Create volume mount points for persistent data
VOLUME ["/app/storage", "/app/logs"]

# Switch to non-root user
USER tileshop

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/system/health || exit 1

# Start the application with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "dashboard_app:app"]