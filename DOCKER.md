# StoryQuest Docker Guide

Complete guide to running StoryQuest with Docker.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Development Mode](#development-mode)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Topics](#advanced-topics)

---

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- (Optional) Ollama for local LLM

### Basic Usage

1. **Start the application:**
```bash
docker-compose up -d
```

2. **View logs:**
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

3. **Stop the application:**
```bash
docker-compose down
```

4. **Stop and remove volumes (fresh start):**
```bash
docker-compose down -v
```

---

## Architecture

The Docker setup consists of:

### Services

**Backend Service (`backend`)**
- FastAPI application
- Exposed on port 8000
- Persistent SQLite database via volume
- Health checks every 30s
- Auto-restart on failure

**Frontend Service (`frontend`)**
- React app built with Vite
- Served by Nginx
- Exposed on port 3000 (mapped to container port 80)
- Health checks every 30s
- Auto-restart on failure

### Volumes

**`storyquest-data`**
- Stores SQLite database
- Persists between container restarts
- Located at `/app/data` in backend container

### Networks

**`storyquest-network`**
- Bridge network connecting services
- Allows frontend to communicate with backend

---

## Configuration

### Environment Variables

Configuration is managed via `.env` file:

1. **Copy the example:**
```bash
cp .env.example .env
```

2. **Edit for your setup:**
```bash
nano .env  # or your preferred editor
```

### LLM Provider Configuration

**Ollama (Local - Default):**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b
```

**OpenAI (Cloud):**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Anthropic (Cloud):**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
```

**Gemini (Cloud):**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-your-key-here
GEMINI_MODEL=gemini-1.5-flash
```

**OpenRouter (Cloud Aggregator):**
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-haiku
OPENROUTER_SITE_URL=https://storyquest.local
OPENROUTER_APP_NAME=StoryQuest
```

### Safety Configuration

```bash
USE_ENHANCED_FILTER=true
USE_MODERATION_API=false
LOG_VIOLATIONS=true
ENABLE_RATE_LIMITING=true
```

### Applying Changes

After editing `.env`:
```bash
docker-compose down
docker-compose up -d
```

---

## Development Mode

For development with hot-reloading:

### Backend Development

Mount local code as volume in `docker-compose.yml`:

```yaml
services:
  backend:
    volumes:
      - ./backend/app:/app/app:ro  # Mount source code
      - backend-data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Development

For development, run frontend locally instead of in Docker:

```bash
# Run backend in Docker
docker-compose up -d backend

# Run frontend locally
cd frontend
npm install
npm run dev
```

This gives you hot-reloading and faster iteration.

---

## Production Deployment

### Using PostgreSQL

For production, use PostgreSQL instead of SQLite:

1. **Update `docker-compose.yml`:**

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://storyquest:password@postgres:5432/storyquest
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: storyquest-postgres
    environment:
      - POSTGRES_DB=storyquest
      - POSTGRES_USER=storyquest
      - POSTGRES_PASSWORD=your-secure-password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - storyquest-network

volumes:
  postgres-data:
```

2. **Install PostgreSQL dependencies:**

Update `backend/requirements.txt`:
```
asyncpg>=0.29.0
```

### Security Best Practices

1. **Use secrets for API keys:**
```bash
# Don't commit .env to git
echo ".env" >> .gitignore
```

2. **Update CORS settings:**

Edit `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

3. **Enable HTTPS:**

Use a reverse proxy like Nginx or Traefik with Let's Encrypt.

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## Troubleshooting

### Backend won't start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Missing API key: Check `.env` file
- Database permission error: `docker-compose down -v && docker-compose up -d`
- Port 8000 in use: Change port in `docker-compose.yml`

### Frontend shows connection error

**Verify backend is running:**
```bash
curl http://localhost:8000/health
```

**Check frontend environment:**
```bash
docker-compose exec frontend env | grep VITE_API_URL
```

**Rebuild frontend with correct API URL:**
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Ollama connection fails

**From Docker, use host.docker.internal:**
```bash
# In .env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Verify Ollama is running on host:**
```bash
curl http://localhost:11434/api/tags
```

### Database is locked

**SQLite can't handle concurrent writes well. Solutions:**

1. **Restart the backend:**
```bash
docker-compose restart backend
```

2. **Switch to PostgreSQL** (recommended for production)

### Reset everything

**Complete fresh start:**
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

## Advanced Topics

### Custom Dockerfile Modifications

**Backend: Add system packages**

Edit `backend/Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    your-package-here \
    && rm -rf /var/lib/apt/lists/*
```

**Frontend: Optimize build**

Edit `frontend/Dockerfile`:
```dockerfile
# Use specific Node version
FROM node:18.17-alpine AS builder
```

### Multi-Environment Setup

Create separate compose files:

**`docker-compose.yml`** - Base configuration
**`docker-compose.dev.yml`** - Development overrides
**`docker-compose.prod.yml`** - Production overrides

Run with:
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Health Check Tuning

Adjust in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 60s        # Check every 60 seconds
  timeout: 10s         # Timeout after 10 seconds
  retries: 5           # Retry 5 times before marking unhealthy
  start_period: 60s    # Wait 60s before first check
```

### Backup and Restore

**Backup SQLite database:**
```bash
docker cp storyquest-backend:/app/data/storyquest.db ./backup.db
```

**Restore:**
```bash
docker cp ./backup.db storyquest-backend:/app/data/storyquest.db
docker-compose restart backend
```

**Backup PostgreSQL:**
```bash
docker-compose exec postgres pg_dump -U storyquest storyquest > backup.sql
```

**Restore PostgreSQL:**
```bash
cat backup.sql | docker-compose exec -T postgres psql -U storyquest storyquest
```

### Monitoring

**View resource usage:**
```bash
docker stats storyquest-backend storyquest-frontend
```

**Inspect containers:**
```bash
docker-compose exec backend /bin/bash
docker-compose exec frontend /bin/sh
```

**Check logs with timestamps:**
```bash
docker-compose logs -f --timestamps
```

---

## Docker Commands Reference

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend python scripts/init_db.py

# View running containers
docker-compose ps

# Remove all stopped containers and networks
docker-compose down --remove-orphans

# Update images and restart
docker-compose pull
docker-compose up -d
```

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review `backend/README.md` for API details
- Review `SAFETY.md` for safety configuration
- Open an issue on GitHub

**Remember**: Always check logs first when troubleshooting!
