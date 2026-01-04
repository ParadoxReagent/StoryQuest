/**
 * TTS Configuration
 *
 * Centralized configuration for Text-to-Speech narration.
 * Modify these settings to change the voice and behavior of story narration.
 *
 * KOKORO TTS VOICES (default TTS service):
 * ─────────────────────────────────────────
 * American English (a):
 *   - af_heart (default) - Warm, engaging female voice
 *   - af_bella - Clear, professional female voice
 *   - af_nicole - Soft, gentle female voice
 *   - af_sarah - Bright, energetic female voice
 *   - af_sky - Light, airy female voice
 *   - am_adam - Deep, resonant male voice
 *   - am_michael - Friendly, conversational male voice
 *
 * British English (b):
 *   - bf_emma - British female voice
 *   - bf_isabella - British female voice
 *   - bm_george - British male voice
 *   - bm_lewis - British male voice
 *
 * See full list at: https://huggingface.co/hexgrad/Kokoro-82M
 *
 * CHATTERBOX TTS (alternative, requires NVIDIA GPU):
 * ──────────────────────────────────────────────────
 * Uses different parameters: exaggeration, cfg_weight
 * To use Chatterbox, update docker-compose.yml and set ttsProvider below.
 */

export type TTSProvider = 'kokoro' | 'chatterbox';

// ============================================
// MAIN CONFIGURATION - EDIT THESE VALUES
// ============================================

export const ttsConfig = {
  /**
   * Which TTS provider to use
   * - 'kokoro': Fast, works on CPU/Apple Silicon (default)
   * - 'chatterbox': Higher quality, requires NVIDIA GPU
   */
  provider: 'kokoro' as TTSProvider,

  /**
   * Kokoro TTS Settings
   */
  kokoro: {
    /**
     * Voice ID for Kokoro TTS
     * See voice list above for options
     */
    voice: 'af_heart',

    /**
     * Speech speed multiplier
     * Range: 0.5 (slow) to 2.0 (fast)
     * Default: 1.0
     */
    speed: 1.0,
  },

  /**
   * Chatterbox TTS Settings (if using Chatterbox instead)
   */
  chatterbox: {
    /**
     * Emotion/exaggeration level
     * Range: 0.0 (neutral) to 1.0 (very expressive)
     * Default: 0.5
     */
    exaggeration: 0.5,

    /**
     * CFG weight for generation quality
     * Range: 0.0 to 1.0
     * Higher values = more consistent but less natural
     * Default: 0.5
     */
    cfgWeight: 0.5,

    /**
     * Voice cloning audio file (optional)
     * Place audio files in tts-chatterbox/voices/ directory
     * Set to the filename to use voice cloning, or null for default voice
     *
     * Example: 'narrator.wav' (file at tts-chatterbox/voices/narrator.wav)
     *
     * Tips for voice cloning:
     * - Use 5-15 seconds of clear speech audio
     * - WAV or MP3 format supported
     * - Clean audio without background noise works best
     * - voiceAudio: 'your-voice.wav',  // filename of your audio sample
     */
    voiceAudio: null as string | null,
  },
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get the request body for TTS synthesis based on current provider
 */
export function getTTSRequestBody(text: string): Record<string, unknown> {
  if (ttsConfig.provider === 'kokoro') {
    return {
      text,
      voice: ttsConfig.kokoro.voice,
      speed: ttsConfig.kokoro.speed,
    };
  } else {
    const body: Record<string, unknown> = {
      text,
      exaggeration: ttsConfig.chatterbox.exaggeration,
      cfg_weight: ttsConfig.chatterbox.cfgWeight,
    };
    // Include voice_audio only if set (for voice cloning)
    if (ttsConfig.chatterbox.voiceAudio) {
      body.voice_audio = ttsConfig.chatterbox.voiceAudio;
    }
    return body;
  }
}

export default ttsConfig;
