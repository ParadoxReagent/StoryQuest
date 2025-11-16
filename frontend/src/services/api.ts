/**
 * API Client for StoryQuest Backend
 * Phase 4: Web UI
 */

import axios, { AxiosError } from 'axios';
import type {
  StartStoryRequest,
  ContinueStoryRequest,
  StoryResponse,
  SessionHistory,
  ApiError,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds (LLM generation can be slow)
});

/**
 * Start a new story session
 */
export async function startStory(request: StartStoryRequest): Promise<StoryResponse> {
  try {
    const response = await api.post<StoryResponse>('/api/v1/story/start', request);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}

/**
 * Continue an existing story
 */
export async function continueStory(request: ContinueStoryRequest): Promise<StoryResponse> {
  try {
    const response = await api.post<StoryResponse>('/api/v1/story/continue', request);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}

/**
 * Get session history
 */
export async function getSessionHistory(sessionId: string): Promise<SessionHistory> {
  try {
    const response = await api.get<SessionHistory>(`/api/v1/story/session/${sessionId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}

/**
 * Reset a session
 */
export async function resetSession(sessionId: string): Promise<void> {
  try {
    await api.post('/api/v1/story/reset', null, {
      params: { session_id: sessionId },
    });
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}

/**
 * Check API health
 */
export async function healthCheck(): Promise<{ status: string; service: string }> {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}

/**
 * Streaming event types
 */
export interface StreamEvent {
  type: 'session_start' | 'text_chunk' | 'complete' | 'error';
  session_id?: string;
  content?: string;
  choices?: Array<{ choice_id: string; text: string }>;
  scene_text?: string;
  story_summary?: string;
  metadata?: {
    theme: string;
    turns: number;
    session_id: string;
    max_turns?: number;
    is_finished?: boolean;
  };
  message?: string;
}

export interface StreamCallbacks {
  onSessionStart?: (sessionId: string) => void;
  onTextChunk?: (chunk: string) => void;
  onComplete?: (choices: any[], metadata: any, sceneText?: string, storySummary?: string) => void;
  onError?: (error: string) => void;
}

/**
 * Start a new story with streaming
 */
export async function startStoryStream(
  request: StartStoryRequest,
  callbacks: StreamCallbacks
): Promise<void> {
  const url = `${API_BASE_URL}/api/v1/story/start/stream`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove "data: " prefix

          try {
            const event: StreamEvent = JSON.parse(data);

            switch (event.type) {
              case 'session_start':
                if (event.session_id && callbacks.onSessionStart) {
                  callbacks.onSessionStart(event.session_id);
                }
                break;

              case 'text_chunk':
                if (event.content && callbacks.onTextChunk) {
                  callbacks.onTextChunk(event.content);
                }
                break;

              case 'complete':
                if (event.choices && event.metadata && callbacks.onComplete) {
                  callbacks.onComplete(event.choices, event.metadata, event.scene_text, event.story_summary);
                }
                break;

              case 'error':
                if (event.message && callbacks.onError) {
                  callbacks.onError(event.message);
                }
                break;
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Streaming error:', error);
    if (callbacks.onError) {
      callbacks.onError(error instanceof Error ? error.message : 'Unknown streaming error');
    }
    throw error;
  }
}

/**
 * Continue story with streaming
 */
export async function continueStoryStream(
  request: ContinueStoryRequest,
  callbacks: StreamCallbacks
): Promise<void> {
  const url = `${API_BASE_URL}/api/v1/story/continue/stream`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove "data: " prefix

          try {
            const event: StreamEvent = JSON.parse(data);

            switch (event.type) {
              case 'text_chunk':
                if (event.content && callbacks.onTextChunk) {
                  callbacks.onTextChunk(event.content);
                }
                break;

              case 'complete':
                if (event.choices && event.metadata && callbacks.onComplete) {
                  callbacks.onComplete(event.choices, event.metadata, event.scene_text, event.story_summary);
                }
                break;

              case 'error':
                if (event.message && callbacks.onError) {
                  callbacks.onError(event.message);
                }
                break;
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Streaming error:', error);
    if (callbacks.onError) {
      callbacks.onError(error instanceof Error ? error.message : 'Unknown streaming error');
    }
    throw error;
  }
}

/**
 * Handle API errors
 */
function handleApiError(error: unknown): void {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    if (axiosError.response) {
      // Server responded with error
      console.error('API Error:', axiosError.response.data);
    } else if (axiosError.request) {
      // Request made but no response
      console.error('Network Error: No response from server');
    } else {
      // Error in request setup
      console.error('Request Error:', axiosError.message);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}

export default api;
