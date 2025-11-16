# Docker Quick Reference - StoryQuest

## 🚀 Common Commands

### Start & Stop

```bash
# Start all services (detached)
docker-compose up -d

# Start with logs visible
docker-compose up

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Development Mode

```bash
# Start with development overrides (hot-reload backend)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run only backend (run frontend locally with npm run dev)
docker-compose up -d backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Rebuild & Restart

```bash
# Rebuild all images
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Rebuild and restart specific service
docker-compose build backend
docker-compose up -d backend

# Restart without rebuilding
docker-compose restart backend
```

### Status & Inspection

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats storyquest-backend storyquest-frontend

# Execute shell in container
docker-compose exec backend /bin/bash
docker-compose exec frontend /bin/sh
```

### Database Management

```bash
# Backup SQLite database
docker cp storyquest-backend:/app/data/storyquest.db ./backup-$(date +%Y%m%d).db

# Restore database
docker cp ./backup.db storyquest-backend:/app/data/storyquest.db
docker-compose restart backend

# Initialize database manually
docker-compose exec backend python scripts/init_db.py
```

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove everything (images, containers, networks)
docker-compose down --rmi all -v

# Clean up Docker system
docker system prune -a
```

## 🔧 Configuration Changes

### After editing .env file

```bash
docker-compose down
docker-compose up -d
```

### After code changes (without hot-reload)

```bash
docker-compose build
docker-compose up -d
```

### After Dockerfile changes

```bash
docker-compose build --no-cache
docker-compose up -d
```

## 🐛 Troubleshooting

### View detailed logs

```bash
# Backend errors
docker-compose logs backend | grep ERROR

# All logs with timestamps
docker-compose logs -f --timestamps
```

### Check container health

```bash
docker-compose ps
docker inspect storyquest-backend | grep -A 10 Health
```

### Test backend API

```bash
# Health check
curl http://localhost:8000/health

# API root
curl http://localhost:8000/

# View API docs
open http://localhost:8000/docs
```

### Access container shell

```bash
# Backend (Python/bash)
docker-compose exec backend /bin/bash

# Frontend (Nginx/sh)
docker-compose exec frontend /bin/sh

# Run Python commands
docker-compose exec backend python -c "import app.main; print('OK')"
```

### Port conflicts

```bash
# Find what's using port 8000
lsof -i :8000
sudo lsof -i :8000

# Change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use 8001 instead
```

## 📝 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Admin Panel**: http://localhost:8000/api/v1/admin/health/detailed

## 🔐 Using Different LLM Providers

### Ollama (Default - Local)

No configuration needed if Ollama is running on host:
```bash
# Check Ollama is accessible
curl http://localhost:11434/api/tags
```

### OpenAI

Edit `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

### Anthropic

Edit `.env`:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

### Gemini

Edit `.env`:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-your-key-here
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

### OpenRouter

Edit `.env`:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-your-key-here
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

## 📊 Monitoring

### Resource usage

```bash
# Live stats
docker stats storyquest-backend storyquest-frontend

# Disk usage
docker system df

# Volume size
docker volume inspect storyquest-data
```

### Health checks

```bash
# Backend health
curl -s http://localhost:8000/health | jq

# Frontend health
curl -s http://localhost:3000/health

# Admin detailed health
curl -s http://localhost:8000/api/v1/admin/health/detailed | jq
```

## 🎯 Quick Workflows

### First time setup

```bash
git clone <repo>
cd StoryQuest
cp .env.example .env
# Edit .env if needed
docker-compose up -d
```

### Daily development

```bash
# Backend development (hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend

# Frontend development (local)
cd frontend && npm run dev
```

### Full restart

```bash
docker-compose down
docker-compose build
docker-compose up -d
docker-compose logs -f
```

### Clean slate

```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

For detailed documentation, see [DOCKER.md](DOCKER.md)
