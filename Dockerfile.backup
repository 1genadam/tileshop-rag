FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libc6-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Create and set permissions for data directories
RUN mkdir -p instance data logs && \
    chown -R appuser:appuser instance data logs && \
    chmod 755 instance data logs

# Install poetry and add to PATH
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy app files
COPY . .

# Remove unnecessary files for production
RUN rm -rf \
    __pycache__/ \
    *.pyc \
    *.pyo \
    *.pyd \
    .Python \
    env/ \
    venv/ \
    .venv/ \
    pip-wheel-metadata/ \
    .pytest_cache/ \
    .coverage \
    .git/ \
    debug_*.py \
    test_*.py \
    *.log \
    recovery_*.json \
    sitemap.xml

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080
EXPOSE 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/system/health || exit 1

# Production command with gunicorn via poetry
CMD ["poetry", "run", "gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--preload", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "admin_dashboard:app"]