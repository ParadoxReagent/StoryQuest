import { AchievementState, AchievementProgress } from './types';

const STORAGE_KEY = 'storyquest-achievements';
const STORAGE_VERSION = 1;

interface StoredAchievementData {
  version: number;
  state: AchievementState;
}

function getInitialProgress(): AchievementProgress {
  return {
    storiesStarted: 0,
    storiesFinished: 0,
    choicesMade: 0,
    customInputsUsed: 0,
    themesPlayed: [],
    ageRangesPlayed: [],
    longestStoryTurns: 0,
    currentSessionChoices: 0,
    achievementMenuOpens: 0,
    storiesFinishedByLength: [],
  };
}

function getInitialState(): AchievementState {
  return {
    unlocked: [],
    progress: getInitialProgress(),
  };
}

export const achievementStorage = {
  load(): AchievementState {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return getInitialState();

      const data: StoredAchievementData = JSON.parse(raw);

      // Handle version migrations if needed
      if (data.version !== STORAGE_VERSION) {
        return migrateState(data);
      }

      // Ensure all progress fields exist (handles missing fields from older versions)
      return {
        ...data.state,
        progress: {
          ...getInitialProgress(),
          ...data.state.progress,
        },
      };
    } catch (e) {
      console.error('Failed to load achievements:', e);
      return getInitialState();
    }
  },

  save(state: AchievementState): void {
    try {
      const data: StoredAchievementData = {
        version: STORAGE_VERSION,
        state,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      console.error('Failed to save achievements:', e);
    }
  },

  clear(): void {
    localStorage.removeItem(STORAGE_KEY);
  },
};

function migrateState(data: StoredAchievementData): AchievementState {
  // Future migration logic - for now, just return with initial progress merged
  return {
    unlocked: data.state?.unlocked || [],
    progress: {
      ...getInitialProgress(),
      ...(data.state?.progress || {}),
    },
  };
}
