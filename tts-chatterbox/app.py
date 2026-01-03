"""
Chatterbox TTS Service - FastAPI wrapper for Resemble AI's Chatterbox TTS.
"""

import io
import os
import hashlib
import logging
from pathlib import Path
from contextlib import asynccontextmanager

import torch
import torchaudio as ta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
tts_model = None


class TTSRequest(BaseModel):
    """Request model for TTS generation."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    exaggeration: float = Field(default=0.5, ge=0.0, le=1.0, description="Emotion exaggeration level")
    cfg_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="CFG weight for generation")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    device: str


def get_cache_path(text: str, exaggeration: float, cfg_weight: float) -> Path:
    """Generate a cache file path based on request parameters."""
    cache_dir = Path("/app/cache")
    cache_dir.mkdir(exist_ok=True)

    # Create hash of parameters for cache key
    cache_key = hashlib.md5(
        f"{text}:{exaggeration}:{cfg_weight}".encode()
    ).hexdigest()

    return cache_dir / f"{cache_key}.wav"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load TTS model on startup."""
    global tts_model

    logger.info("Loading Chatterbox TTS model...")

    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    if device == "cpu":
        logger.warning("GPU not available - TTS will be slower on CPU")

    try:
        # Import and load the model
        from chatterbox.tts import ChatterboxTTS
        tts_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info("Chatterbox TTS model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down TTS service")
    tts_model = None


app = FastAPI(
    title="StoryQuest TTS Service",
    description="Text-to-Speech service using Chatterbox TTS for story narration",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return HealthResponse(
        status="healthy" if tts_model is not None else "unhealthy",
        model_loaded=tts_model is not None,
        device=device,
    )


@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text.

    Returns audio as WAV file.
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not loaded")

    # Check cache first
    cache_path = get_cache_path(request.text, request.exaggeration, request.cfg_weight)

    if cache_path.exists():
        logger.info(f"Cache hit for text: {request.text[:50]}...")
        with open(cache_path, "rb") as f:
            audio_bytes = f.read()
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=narration.wav"}
        )

    logger.info(f"Generating speech for: {request.text[:50]}...")

    try:
        # Generate audio
        wav = tts_model.generate(
            request.text,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight,
        )

        # Save to buffer
        buffer = io.BytesIO()
        ta.save(buffer, wav, tts_model.sr, format="wav")
        buffer.seek(0)

        # Cache the result
        audio_bytes = buffer.read()
        with open(cache_path, "wb") as f:
            f.write(audio_bytes)

        logger.info("Speech synthesis complete")

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=narration.wav"}
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.delete("/cache")
async def clear_cache():
    """Clear the TTS cache."""
    cache_dir = Path("/app/cache")
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(exist_ok=True)
    return {"status": "cache cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
