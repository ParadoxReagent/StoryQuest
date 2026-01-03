# Kokoro TTS Service Dockerfile
# Lightweight TTS optimized for CPU and Apple Silicon (MPS)
# Much faster than Chatterbox on non-CUDA systems

FROM python:3.11-slim-bookworm

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Enable MPS fallback for Apple Silicon
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# Install system dependencies
# espeak-ng is required by Kokoro for phoneme processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    espeak-ng \
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
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Copy application code
COPY app.py .

# Create cache directory and set ownership
RUN mkdir -p /app/cache \
    && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check - shorter start period since Kokoro loads faster
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
