/**
 * TypeScript types for StoryQuest API
 * Phase 4: Web UI
 */

export interface Choice {
  choice_id: string;
  text: string;
}

export interface Scene {
  scene_id: string;
  text: string;
  timestamp: string;
}

export interface StoryMetadata {
  turns: number;
  theme: string;
  age_range: string;
  max_turns?: number;
  is_finished?: boolean;
}

export interface StoryResponse {
  session_id: string;
  story_summary: string;
  current_scene: Scene;
  choices: Choice[];
  metadata?: StoryMetadata;
}

export interface StartStoryRequest {
  player_name: string;
  age_range: string;
  theme: string;
}

export interface ContinueStoryRequest {
  session_id: string;
  choice_id?: string;
  choice_text?: string;
  custom_input?: string;
  story_summary: string;
}

export interface SessionHistory {
  session_id: string;
  player_name: string;
  age_range: string;
  theme: string;
  created_at: string;
  last_activity: string;
  total_turns: number;
  is_active: boolean;
  turns: Array<{
    turn_number: number;
    scene_text: string;
    scene_id: string;
    player_choice?: string;
    custom_input?: string;
    story_summary: string;
    created_at: string;
  }>;
}

export interface ApiError {
  detail: string;
}
