# Railway Deployment - BMAD MCP Server v2.0
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/
COPY config/ ./config/

# Install package in editable mode
RUN pip install -e .

# Set Python path
ENV PYTHONPATH=/app/src

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose Railway port
EXPOSE $PORT

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Railway compatible start command
CMD ["python", "-m", "bmad_mcp.server", "--port", "$PORT", "--host", "0.0.0.0"]