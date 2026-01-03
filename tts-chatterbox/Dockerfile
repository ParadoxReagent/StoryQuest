# Chatterbox TTS Service Dockerfile
# Supports both ARM (Apple Silicon) and x86_64 architectures
# Runs on CPU by default; GPU acceleration available on NVIDIA systems

FROM python:3.11-slim-bookworm

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies as root (safe during build)
RUN pip install --no-cache-dir --upgrade pip --root-user-action=ignore \
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy application code
COPY app.py .

# Create cache directory and set ownership
RUN mkdir -p /app/cache \
    && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
