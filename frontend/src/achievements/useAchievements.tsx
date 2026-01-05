import { useState, useCallback, useEffect, useRef } from 'react';
import { toast } from 'sonner';
import { AchievementState, AchievementId, Achievement } from './types';
import { ACHIEVEMENTS, TOTAL_ACHIEVEMENTS } from './definitions';
import { achievementStorage } from './achievementStorage';
import { AchievementToast } from './AchievementToast';

export function useAchievements() {
  const [state, setState] = useState<AchievementState>(() =>
    achievementStorage.load()
  );
  const pendingToastsRef = useRef<AchievementId[]>([]);
  const isProcessingToastRef = useRef(false);

  // Save to localStorage whenever state changes
  useEffect(() => {
    achievementStorage.save(state);
  }, [state]);

  // Process pending toasts one at a time
  useEffect(() => {
    if (pendingToastsRef.current.length > 0 && !isProcessingToastRef.current) {
      isProcessingToastRef.current = true;
      const toShow = pendingToastsRef.current.shift();
      if (toShow) {
        const achievement = state.unlocked.find((a) => a.id === toShow);
        if (achievement) {
          toast.custom(
            (t) => <AchievementToast achievement={achievement} toastId={t} />,
            {
              duration: 5000,
              position: 'top-center',
              onDismiss: () => {
                isProcessingToastRef.current = false;
              },
              onAutoClose: () => {
                isProcessingToastRef.current = false;
              },
            }
          );
          // Fallback in case callbacks don't fire
          setTimeout(() => {
            isProcessingToastRef.current = false;
          }, 5500);
        } else {
          isProcessingToastRef.current = false;
        }
      }
    }
  }, [state.unlocked]);

  // Check if achievement is already unlocked
  const isUnlocked = useCallback(
    (id: AchievementId) => state.unlocked.some((a) => a.id === id),
    [state.unlocked]
  );

  // Try to unlock an achievement
  const tryUnlock = useCallback(
    (id: AchievementId) => {
      setState((prev) => {
        // Already unlocked
        if (prev.unlocked.some((a) => a.id === id)) {
          return prev;
        }

        const achievement: Achievement = {
          ...ACHIEVEMENTS[id],
          unlockedAt: Date.now(),
        };

        // Queue toast for after state update
        pendingToastsRef.current.push(id);

        return {
          ...prev,
          unlocked: [...prev.unlocked, achievement],
        };
      });
    },
    []
  );

  // Track when a story starts
  const trackStoryStarted = useCallback(
    (theme: string, ageRange: string) => {
      setState((prev) => {
        const newThemes = prev.progress.themesPlayed.includes(theme)
          ? prev.progress.themesPlayed
          : [...prev.progress.themesPlayed, theme];

        const newAgeRanges = prev.progress.ageRangesPlayed.includes(ageRange)
          ? prev.progress.ageRangesPlayed
          : [...prev.progress.ageRangesPlayed, ageRange];

        return {
          ...prev,
          progress: {
            ...prev.progress,
            storiesStarted: prev.progress.storiesStarted + 1,
            themesPlayed: newThemes,
            ageRangesPlayed: newAgeRanges,
            currentSessionChoices: 0, // Reset for new story
          },
        };
      });

      // Check achievements after state update
      setTimeout(() => {
        tryUnlock('first_story_started');

        // Time-based achievements
        const hour = new Date().getHours();
        const day = new Date().getDay();

        // Night owl: after 9pm (21:00)
        if (hour >= 21) {
          tryUnlock('night_owl');
        }

        // Early bird: before 8am
        if (hour < 8) {
          tryUnlock('early_bird');
        }

        // Weekend warrior: Saturday (6) or Sunday (0)
        if (day === 0 || day === 6) {
          tryUnlock('weekend_warrior');
        }
      }, 0);
    },
    [tryUnlock]
  );

  // Track when a choice is made
  const trackChoiceMade = useCallback(
    (turnNumber: number) => {
      setState((prev) => ({
        ...prev,
        progress: {
          ...prev.progress,
          choicesMade: prev.progress.choicesMade + 1,
          longestStoryTurns: Math.max(
            prev.progress.longestStoryTurns,
            turnNumber
          ),
          currentSessionChoices: prev.progress.currentSessionChoices + 1,
        },
      }));

      // Check achievements after state update
      setTimeout(() => {
        tryUnlock('first_choice_made');
      }, 0);
    },
    [tryUnlock]
  );

  // Track when custom input is used
  const trackCustomInput = useCallback(() => {
    setState((prev) => ({
      ...prev,
      progress: {
        ...prev.progress,
        customInputsUsed: prev.progress.customInputsUsed + 1,
      },
    }));

    setTimeout(() => {
      tryUnlock('used_custom_input');
    }, 0);
  }, [tryUnlock]);

  // Track when a story is finished
  const trackStoryFinished = useCallback(
    (totalTurns: number) => {
      setState((prev) => {
        // Track unique story lengths for chapter_champion
        const newLengths = prev.progress.storiesFinishedByLength.includes(totalTurns)
          ? prev.progress.storiesFinishedByLength
          : [...prev.progress.storiesFinishedByLength, totalTurns];

        return {
          ...prev,
          progress: {
            ...prev.progress,
            storiesFinished: prev.progress.storiesFinished + 1,
            longestStoryTurns: Math.max(
              prev.progress.longestStoryTurns,
              totalTurns
            ),
            storiesFinishedByLength: newLengths,
          },
        };
      });

      setTimeout(() => {
        tryUnlock('first_story_finished');

        // Marathon story: 12+ turns
        if (totalTurns >= 12) {
          tryUnlock('marathon_story');
        }
      }, 0);
    },
    [tryUnlock]
  );

  // Check milestone achievements based on current progress
  const checkMilestones = useCallback(() => {
    const { progress, unlocked } = state;

    // ==================
    // BEGINNER MILESTONES
    // ==================

    // Brave heart: 10 choices made
    if (progress.choicesMade >= 10) {
      tryUnlock('brave_heart');
    }

    // Triple threat: 3 stories finished
    if (progress.storiesFinished >= 3) {
      tryUnlock('triple_threat');
    }

    // ==================
    // EXPLORER MILESTONES
    // ==================

    // Theme exploration (3 themes)
    if (progress.themesPlayed.length >= 3) {
      tryUnlock('three_themes_explored');
    }

    // Theme master (5 themes)
    if (progress.themesPlayed.length >= 5) {
      tryUnlock('theme_master');
    }

    // Long story (10+ turns)
    if (progress.longestStoryTurns >= 10) {
      tryUnlock('long_story');
    }

    // Age range diversity (2+ different age ranges)
    if (progress.ageRangesPlayed.length >= 2) {
      tryUnlock('played_all_age_ranges');
    }

    // Imagination unleashed (5 custom inputs)
    if (progress.customInputsUsed >= 5) {
      tryUnlock('imagination_unleashed');
    }

    // ==================
    // VETERAN MILESTONES
    // ==================

    // Stories started milestones
    if (progress.storiesStarted >= 10) {
      tryUnlock('ten_stories_started');
    }

    if (progress.storiesStarted >= 25) {
      tryUnlock('storyteller_supreme');
    }

    // Stories finished milestones
    if (progress.storiesFinished >= 5) {
      tryUnlock('five_stories_finished');
    }

    if (progress.storiesFinished >= 10) {
      tryUnlock('completionist');
    }

    // Century club (100 choices)
    if (progress.choicesMade >= 100) {
      tryUnlock('century_club');
    }

    // Age master (all 4 age ranges)
    if (progress.ageRangesPlayed.length >= 4) {
      tryUnlock('age_master');
    }

    // Prolific writer (10 custom inputs)
    if (progress.customInputsUsed >= 10) {
      tryUnlock('prolific_writer');
    }

    // ==================
    // SPECIAL MILESTONES
    // ==================

    // Quick reader (5+ choices in one session)
    if (progress.currentSessionChoices >= 5) {
      tryUnlock('quick_reader');
    }

    // Creative writer (3+ custom inputs)
    if (progress.customInputsUsed >= 3) {
      tryUnlock('creative_writer');
    }

    // Bookworm (50 choices)
    if (progress.choicesMade >= 50) {
      tryUnlock('bookworm');
    }

    // Curious cat (10 achievement menu opens)
    if (progress.achievementMenuOpens >= 10) {
      tryUnlock('curious_cat');
    }

    // Halfway hero (50% of achievements)
    const totalAchievements = Object.keys(ACHIEVEMENTS).length;
    if (unlocked.length >= Math.floor(totalAchievements / 2)) {
      tryUnlock('halfway_hero');
    }

    // Dedicated fan (15 stories finished)
    if (progress.storiesFinished >= 15) {
      tryUnlock('dedicated_fan');
    }

    // Chapter champion (3 different story lengths)
    if (progress.storiesFinishedByLength.length >= 3) {
      tryUnlock('chapter_champion');
    }

    // Tale weaver (50 stories started)
    if (progress.storiesStarted >= 50) {
      tryUnlock('tale_weaver');
    }
  }, [state, tryUnlock]);

  // Run milestone checks after progress updates
  useEffect(() => {
    checkMilestones();
  }, [state.progress, checkMilestones]);

  // Reset all achievements and progress
  const resetAchievements = useCallback(() => {
    achievementStorage.clear();
    setState({
      unlocked: [],
      progress: {
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
      },
    });
  }, []);

  // Track when achievement menu is opened
  const trackAchievementMenuOpen = useCallback(() => {
    setState((prev) => ({
      ...prev,
      progress: {
        ...prev.progress,
        achievementMenuOpens: prev.progress.achievementMenuOpens + 1,
      },
    }));
  }, []);

  return {
    state,
    trackStoryStarted,
    trackChoiceMade,
    trackCustomInput,
    trackStoryFinished,
    trackAchievementMenuOpen,
    isUnlocked,
    unlockedCount: state.unlocked.length,
    totalCount: TOTAL_ACHIEVEMENTS,
    resetAchievements,
  };
}
