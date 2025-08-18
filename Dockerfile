# BMAD MCP Server - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Install package
RUN pip install -e .

# Expose port for HTTP mode (optional)
EXPOSE 3000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV BMAD_CONFIG_PATH=/app/config/bmad-core

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from src.bmad_mcp.routing.openrouter import OpenRouterClient; print('OK')" || exit 1

# Default command (stdio mode)
CMD ["python", "-m", "bmad_mcp.server"]