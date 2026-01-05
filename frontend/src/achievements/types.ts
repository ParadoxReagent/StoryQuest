/**
 * Achievement IDs - Add new achievement IDs here
 *
 * When adding a new achievement:
 * 1. Add the ID to this type (use snake_case)
 * 2. Add the definition in definitions.ts
 * 3. Add the unlock trigger in useAchievements.tsx
 */
export type AchievementId =
  // Beginner - Very easy, immediate rewards
  | 'first_story_started'
  | 'first_choice_made'
  | 'first_story_finished'
  | 'brave_heart'
  | 'triple_threat'
  // Explorer - Easy, light exploration
  | 'three_themes_explored'
  | 'used_custom_input'
  | 'long_story'
  | 'played_all_age_ranges'
  | 'night_owl'
  | 'early_bird'
  | 'weekend_warrior'
  | 'theme_master'
  | 'marathon_story'
  | 'imagination_unleashed'
  // Veteran - Medium, returning players
  | 'five_stories_finished'
  | 'ten_stories_started'
  | 'century_club'
  | 'storyteller_supreme'
  | 'completionist'
  | 'age_master'
  | 'prolific_writer'
  // Special - Fun extras
  | 'quick_reader'
  | 'creative_writer'
  | 'bookworm'
  | 'curious_cat'
  | 'halfway_hero'
  | 'dedicated_fan'
  | 'chapter_champion'
  | 'tale_weaver';

export type AchievementTier = 'beginner' | 'explorer' | 'veteran' | 'special';

export interface Achievement {
  id: AchievementId;
  name: string;
  description: string;
  tier: AchievementTier;
  icon: string;
  unlockedAt?: number;
}

export interface AchievementProgress {
  storiesStarted: number;
  storiesFinished: number;
  choicesMade: number;
  customInputsUsed: number;
  themesPlayed: string[];
  ageRangesPlayed: string[];
  longestStoryTurns: number;
  currentSessionChoices: number;
  achievementMenuOpens: number;
  storiesFinishedByLength: number[]; // Track lengths of finished stories
}

export interface AchievementState {
  unlocked: Achievement[];
  progress: AchievementProgress;
}

export interface TierColors {
  border: string;
  background: string;
  glow: string;
}
