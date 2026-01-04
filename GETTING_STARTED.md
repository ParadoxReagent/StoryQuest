# Getting Started with StoryQuest

Welcome to StoryQuest! This guide will help you get up and running quickly.

## 🐳 Docker Setup (Recommended)

StoryQuest is designed to run with Docker for the easiest setup and deployment.

### Why Docker?

- ✅ **No manual setup** - No need to install Python, Node.js, or manage dependencies
- ✅ **Consistent environment** - Works the same on macOS, Windows, and Linux
- ✅ **Production-ready** - Same setup for development and deployment
- ✅ **Easy updates** - Pull latest changes and rebuild with one command
- ✅ **Isolated** - Doesn't interfere with your system

### Quick Start (5 minutes)

**1. Install Docker Desktop**

Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your platform.

**2. Clone the repository**

```bash
git clone <repository-url>
cd StoryQuest
```

**3. (Optional) Configure LLM provider**

By default, StoryQuest uses Ollama (local LLM). To use cloud providers:

```bash
cp .env.example .env
# Edit .env to set your API key
```

For OpenAI:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

For Anthropic:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

For Gemini:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-your-key-here
```

For OpenRouter:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-your-key-here
```

**4. Start the application**

```bash
docker-compose up -d
```

That's it! The application is now running.

**5. Open StoryQuest**

Open your web browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### Daily Usage

**Start the application:**
```bash
docker-compose up -d
```

**Stop the application:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Update to latest version:**
```bash
git pull
docker-compose build
docker-compose up -d
```

---

## 🔧 Using with Ollama (Local LLM)

If you want to use a local LLM with Ollama:

**1. Install Ollama**

Download from [https://ollama.ai](https://ollama.ai)

**2. Pull a model**

```bash
ollama pull llama3.2:3b
```

**3. Start StoryQuest**

```bash
docker-compose up -d
```

The backend automatically connects to Ollama running on your host machine.

---

## 🎯 Using the Application

### Starting a Story

1. Open http://localhost:3000
2. Enter your name
3. Use the age slider (5-18) to set your reading level:
   - **5-7**: Early Reader (Wonder & Friendship)
   - **8-10**: Middle Reader (Action & Bravery)
   - **11-13**: Tween (Moral Dilemmas)
   - **14-18**: Young Adult (Complex Themes)
4. Choose from the generated adventure themes
5. Click "Begin Your Quest!"

### Playing

1. Read the scene description (or click the speaker button for narration)
2. Choose one of the suggested options, or type your own idea
3. Watch the story continue based on your choice!
4. Click "Story So Far" to review your adventure
5. Click "New Story" to start over

---

## 📚 Documentation

- **[DOCKER.md](DOCKER.md)** - Complete Docker guide with advanced usage
- **[DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md)** - Quick command reference
- **[backend/README.md](backend/README.md)** - Backend API documentation
- **[frontend/README.md](frontend/README.md)** - Frontend development guide
- **[backend/SAFETY.md](backend/SAFETY.md)** - Safety features and content moderation

---

## 🛠️ Development

### Hot-Reload Development Mode

For development with automatic code reloading:

```bash
# Backend with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
```

### Frontend Development

For frontend development, it's often faster to run the frontend locally:

```bash
# Keep backend in Docker
docker-compose up -d backend

# Run frontend locally
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Access backend shell
docker-compose exec backend /bin/bash
```

---

## 🚨 Troubleshooting

### Backend won't start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Port 8000 already in use - Stop other services or change port in docker-compose.yml
- Missing API key - Check .env file if using cloud LLMs
- Database locked - Run `docker-compose down -v` and try again

### Frontend shows connection error

**Verify backend is running:**
```bash
docker-compose ps
curl http://localhost:8000/health
```

**Restart services:**
```bash
docker-compose restart
```

### Ollama connection fails

**Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**Verify configuration:**
- Make sure Ollama is running on your host machine
- The backend connects to `http://host.docker.internal:11434`

### Fresh start

To completely reset everything:
```bash
docker-compose down -v
docker-compose build
docker-compose up -d
```

---

## 💡 Tips

1. **View all logs**: `docker-compose logs -f` to see both backend and frontend
2. **Check health**: Visit http://localhost:8000/health to verify backend is working
3. **Admin endpoints**: Visit http://localhost:8000/api/v1/admin/health/detailed for detailed status
4. **API documentation**: Visit http://localhost:8000/docs for interactive API documentation

---

## 📦 Advanced: Manual Installation

If you cannot use Docker, see the manual installation instructions:

- [Backend Manual Setup](backend/README.md#-manual-installation-advanced)
- [Frontend Manual Setup](frontend/README.md#-manual-installation-advanced)

**Note**: Manual installation is only recommended for development. For production deployment, use Docker.

---

## 🎉 Next Steps

Now that you have StoryQuest running:

1. ✅ Create your first story!
2. ✅ Try different themes and see how the stories change
3. ✅ Experiment with custom inputs to see how creative you can be
4. ✅ Check out the [API documentation](http://localhost:8000/docs)
5. ✅ Read about [safety features](backend/SAFETY.md) that keep stories kid-friendly

---

## ❓ Getting Help

- **Issues**: Open an issue on GitHub
- **Questions**: Check existing documentation
- **Logs**: Always check `docker-compose logs` first

**Happy adventuring! 🚀**
