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
