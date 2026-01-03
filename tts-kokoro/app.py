"""
Kokoro TTS Service - FastAPI wrapper for Kokoro TTS.
Optimized for CPU and Apple Silicon (MPS) - fast and lightweight.
"""

import io
import os
import hashlib
import logging
from pathlib import Path
from contextlib import asynccontextmanager

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
tts_pipeline = None
SAMPLE_RATE = 24000  # Kokoro outputs at 24kHz


class TTSRequest(BaseModel):
    """Request model for TTS generation."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: str = Field(default="af_heart", description="Voice to use for synthesis")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    device: str


def get_cache_path(text: str, voice: str, speed: float) -> Path:
    """Generate a cache file path based on request parameters."""
    cache_dir = Path("/app/cache")
    cache_dir.mkdir(exist_ok=True)

    # Create hash of parameters for cache key
    cache_key = hashlib.md5(
        f"{text}:{voice}:{speed}".encode()
    ).hexdigest()

    return cache_dir / f"{cache_key}.wav"


def get_device() -> str:
    """Determine the best available device."""
    import torch
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load TTS pipeline on startup."""
    global tts_pipeline

    logger.info("Loading Kokoro TTS pipeline...")

    device = get_device()
    logger.info(f"Using device: {device}")

    try:
        from kokoro import KPipeline
        # Use American English by default, explicitly set repo_id to suppress warning
        tts_pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
        logger.info("Kokoro TTS pipeline loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load TTS pipeline: {e}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down TTS service")
    tts_pipeline = None


app = FastAPI(
    title="StoryQuest TTS Service (Kokoro)",
    description="Text-to-Speech service using Kokoro TTS for story narration - optimized for CPU/MPS",
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
    device = get_device()
    return HealthResponse(
        status="healthy" if tts_pipeline is not None else "unhealthy",
        model_loaded=tts_pipeline is not None,
        device=device,
    )


@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text.

    Returns audio as WAV file.
    """
    if tts_pipeline is None:
        raise HTTPException(status_code=503, detail="TTS pipeline not loaded")

    # Check cache first
    cache_path = get_cache_path(request.text, request.voice, request.speed)

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
        # Generate audio using Kokoro pipeline
        # The pipeline returns a generator of (graphemes, phonemes, audio) tuples
        audio_chunks = []
        generator = tts_pipeline(
            request.text,
            voice=request.voice,
            speed=request.speed,
        )

        for gs, ps, audio in generator:
            if audio is not None:
                audio_chunks.append(audio)

        if not audio_chunks:
            raise HTTPException(status_code=500, detail="No audio generated")

        # Concatenate all audio chunks
        full_audio = np.concatenate(audio_chunks)

        # Save to buffer as WAV
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, SAMPLE_RATE, format='WAV')
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
