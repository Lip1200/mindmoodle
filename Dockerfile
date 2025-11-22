# Multi-stage build for Mental Health Chatbot
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Production stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY app.py .
COPY chainlit.md .
COPY .chainlit/ .chainlit/
COPY public/ public/

# Create non-root user for security
RUN useradd -m -u 1000 chainlit && \
    chown -R chainlit:chainlit /app

USER chainlit

# Expose Chainlit port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Run Chainlit
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
