# StoryQuest Quick Start Guide

Get StoryQuest up and running in minutes!

## Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **(Optional)** Ollama for local LLM

## Step 1: Backend Setup (5 minutes)

### Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if using cloud LLMs:
```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=ai-your-key-here

# For OpenRouter
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=or-your-key-here
```

For local LLM (Ollama), keep the default `LLM_PROVIDER=ollama`.

### Initialize Database

```bash
python scripts/init_db.py
```

### Start Backend Server

```bash
python -m uvicorn app.main:app --reload
```

The API is now running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## Step 2: Frontend Setup (2 minutes)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The web app is now running at: **http://localhost:3000**

## Step 3: Using Ollama (Optional)

If you want to use a local LLM:

1. Install Ollama from https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Make sure `LLM_PROVIDER=ollama` in your `.env` file
4. Restart the backend server

## Step 4: Start Playing!

1. Open http://localhost:3000 in your browser
2. Enter your name
3. Use the age slider (5-18) to set your reading level:
   - **5-7**: Early Reader (Wonder & Friendship)
   - **8-10**: Middle Reader (Action & Bravery)
   - **11-13**: Tween (Moral Dilemmas)
   - **14-18**: Young Adult (Complex Themes)
4. Pick from the generated adventure themes
5. Click "Begin Your Quest!"
6. Enjoy your interactive story with optional text-to-speech narration!

## Troubleshooting

### Backend won't start

- **Check Python version**: `python3 --version` (must be 3.11+)
- **Activate virtual environment**: Make sure you see `(venv)` in your terminal
- **Check port 8000**: Make sure nothing else is using port 8000

### Frontend won't start

- **Check Node version**: `node --version` (must be 18+)
- **Clear cache**: Delete `node_modules` and run `npm install` again
- **Check port 3000**: Make sure nothing else is using port 3000

### LLM generation fails

- **Ollama**: Make sure Ollama is running: `ollama list`
- **OpenAI/Anthropic/Gemini/OpenRouter**: Verify your API key is correct in `.env`
- **Check logs**: Look at the backend terminal for error messages

### Database errors

- **Reinitialize**: Run `python scripts/init_db.py` again
- **Delete database**: Remove `storyquest.db` and reinitialize

## Next Steps

- **Change LLM provider**: Edit `config.yaml` or set environment variables
- **Customize themes**: Modify `backend/app/services/prompts.py`
- **Adjust safety filters**: Edit `backend/app/services/safety_filter.py`
- **Style the UI**: Modify `frontend/src/index.css` and Tailwind config

## Getting Help

- **Backend docs**: See `backend/README.md`
- **Frontend docs**: See `frontend/README.md`
- **API documentation**: http://localhost:8000/docs (when running)
- **Project plan**: See `StoryQuest_Plan.md`

Happy adventuring! ✨
