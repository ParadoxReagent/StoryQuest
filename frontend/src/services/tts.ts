/**
 * TTS Service Client for StoryQuest
 * Connects to the Chatterbox TTS Docker service for story narration
 */

const TTS_BASE_URL = import.meta.env.VITE_TTS_URL || 'http://localhost:8001';

export interface TTSRequest {
  text: string;
  exaggeration?: number;  // 0.0-1.0, emotion level
  cfg_weight?: number;    // 0.0-1.0, generation weight
}

export interface TTSHealthResponse {
  status: string;
  model_loaded: boolean;
  device: string;
}

/**
 * Check TTS service health
 */
export async function checkTTSHealth(): Promise<TTSHealthResponse> {
  const response = await fetch(`${TTS_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`TTS health check failed: ${response.status}`);
  }
  return response.json();
}

/**
 * Generate speech audio from text
 * Returns a blob URL that can be used with an audio element
 */
export async function synthesizeSpeech(request: TTSRequest): Promise<string> {
  const response = await fetch(`${TTS_BASE_URL}/synthesize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: request.text,
      exaggeration: request.exaggeration ?? 0.5,
      cfg_weight: request.cfg_weight ?? 0.5,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `TTS synthesis failed: ${response.status}`);
  }

  const audioBlob = await response.blob();
  return URL.createObjectURL(audioBlob);
}

/**
 * TTS Audio Player class for managing playback state
 */
export class TTSPlayer {
  private audio: HTMLAudioElement | null = null;
  private currentBlobUrl: string | null = null;
  private onStateChange: ((state: TTSPlaybackState) => void) | null = null;

  constructor(onStateChange?: (state: TTSPlaybackState) => void) {
    this.onStateChange = onStateChange ?? null;
  }

  private updateState(state: TTSPlaybackState) {
    if (this.onStateChange) {
      this.onStateChange(state);
    }
  }

  /**
   * Play narration for the given text
   */
  async play(text: string): Promise<void> {
    // Stop any existing playback
    this.stop();

    this.updateState({ isLoading: true, isPlaying: false, error: null });

    try {
      // Generate audio
      const blobUrl = await synthesizeSpeech({ text });
      this.currentBlobUrl = blobUrl;

      // Create and configure audio element
      this.audio = new Audio(blobUrl);

      // Set up event listeners
      this.audio.addEventListener('playing', () => {
        this.updateState({ isLoading: false, isPlaying: true, error: null });
      });

      this.audio.addEventListener('pause', () => {
        this.updateState({ isLoading: false, isPlaying: false, error: null });
      });

      this.audio.addEventListener('ended', () => {
        this.updateState({ isLoading: false, isPlaying: false, error: null });
        this.cleanup();
      });

      this.audio.addEventListener('error', () => {
        this.updateState({
          isLoading: false,
          isPlaying: false,
          error: 'Audio playback failed',
        });
        this.cleanup();
      });

      // Start playback
      await this.audio.play();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'TTS failed';
      this.updateState({ isLoading: false, isPlaying: false, error: errorMessage });
      this.cleanup();
      throw error;
    }
  }

  /**
   * Pause current playback
   */
  pause(): void {
    if (this.audio && !this.audio.paused) {
      this.audio.pause();
    }
  }

  /**
   * Resume paused playback
   */
  resume(): void {
    if (this.audio && this.audio.paused) {
      this.audio.play();
    }
  }

  /**
   * Stop playback and cleanup
   */
  stop(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
    }
    this.cleanup();
    this.updateState({ isLoading: false, isPlaying: false, error: null });
  }

  /**
   * Toggle play/pause
   */
  toggle(text: string): void {
    if (this.audio && !this.audio.paused) {
      this.pause();
    } else if (this.audio && this.audio.paused && this.currentBlobUrl) {
      this.resume();
    } else {
      this.play(text);
    }
  }

  private cleanup(): void {
    if (this.currentBlobUrl) {
      URL.revokeObjectURL(this.currentBlobUrl);
      this.currentBlobUrl = null;
    }
    this.audio = null;
  }

  /**
   * Cleanup when component unmounts
   */
  destroy(): void {
    this.stop();
  }
}

export interface TTSPlaybackState {
  isLoading: boolean;
  isPlaying: boolean;
  error: string | null;
}

export const initialTTSState: TTSPlaybackState = {
  isLoading: false,
  isPlaying: false,
  error: null,
};
