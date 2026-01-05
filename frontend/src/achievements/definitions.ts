/**
 * ACHIEVEMENTS CONFIGURATION
 * ==========================
 *
 * This file contains all achievement definitions for StoryQuest.
 *
 * HOW TO ADD A NEW ACHIEVEMENT:
 * 1. Add the achievement ID to the `AchievementId` type in `types.ts`
 * 2. Add the achievement definition below with: id, name, description, tier, icon
 * 3. Add the unlock trigger in `useAchievements.tsx` (either immediate or milestone-based)
 *
 * TIERS:
 * - beginner: Very easy, achievable immediately (gold theme)
 * - explorer: Easy, requires light exploration (green theme)
 * - veteran: Medium, for returning players (red/leather theme)
 * - special: Fun extras, unique conditions (bright gold theme)
 *
 * ICONS: Use Unicode emoji codes (e.g., '\u{1F4D6}' for 📖)
 *        Find codes at: https://unicode.org/emoji/charts/full-emoji-list.html
 */

import { Achievement, AchievementId, AchievementTier, TierColors } from './types';

export const ACHIEVEMENTS: Record<AchievementId, Omit<Achievement, 'unlockedAt'>> = {
  // =============================================
  // BEGINNER TIER - Very Easy (achievable quickly)
  // =============================================
  first_story_started: {
    id: 'first_story_started',
    name: 'Once Upon a Time',
    description: 'Started your very first adventure!',
    tier: 'beginner',
    icon: '\u{1F4D6}', // 📖
  },
  first_choice_made: {
    id: 'first_choice_made',
    name: 'Decision Maker',
    description: 'Made your first story choice',
    tier: 'beginner',
    icon: '\u{1F3AF}', // 🎯
  },
  first_story_finished: {
    id: 'first_story_finished',
    name: 'The End',
    description: 'Completed your first story from start to finish',
    tier: 'beginner',
    icon: '\u{1F3C6}', // 🏆
  },
  brave_heart: {
    id: 'brave_heart',
    name: 'Brave Heart',
    description: 'Made 10 choices in your adventures',
    tier: 'beginner',
    icon: '\u{1F9E1}', // 🧡
  },
  triple_threat: {
    id: 'triple_threat',
    name: 'Triple Threat',
    description: 'Finished 3 complete stories',
    tier: 'beginner',
    icon: '\u{1F31F}', // 🌟
  },

  // =============================================
  // EXPLORER TIER - Easy (light exploration)
  // =============================================
  three_themes_explored: {
    id: 'three_themes_explored',
    name: 'Genre Explorer',
    description: 'Tried 3 different story themes',
    tier: 'explorer',
    icon: '\u{1F5FA}', // 🗺️
  },
  used_custom_input: {
    id: 'used_custom_input',
    name: 'Creative Spirit',
    description: 'Wrote your own custom action',
    tier: 'explorer',
    icon: '\u{270D}', // ✍️
  },
  long_story: {
    id: 'long_story',
    name: 'Epic Tale',
    description: 'Experienced a story with 10+ turns',
    tier: 'explorer',
    icon: '\u{1F4DA}', // 📚
  },
  played_all_age_ranges: {
    id: 'played_all_age_ranges',
    name: 'Growing Up',
    description: 'Played stories at different reading levels',
    tier: 'explorer',
    icon: '\u{1F331}', // 🌱
  },
  night_owl: {
    id: 'night_owl',
    name: 'Night Owl',
    description: 'Started a story after 9pm',
    tier: 'explorer',
    icon: '\u{1F989}', // 🦉
  },
  early_bird: {
    id: 'early_bird',
    name: 'Early Bird',
    description: 'Started a story before 8am',
    tier: 'explorer',
    icon: '\u{1F426}', // 🐦
  },
  weekend_warrior: {
    id: 'weekend_warrior',
    name: 'Weekend Warrior',
    description: 'Started a story on a weekend',
    tier: 'explorer',
    icon: '\u{1F389}', // 🎉
  },
  theme_master: {
    id: 'theme_master',
    name: 'Theme Master',
    description: 'Explored 5 different story themes',
    tier: 'explorer',
    icon: '\u{1F3A8}', // 🎨
  },
  marathon_story: {
    id: 'marathon_story',
    name: 'Marathon Reader',
    description: 'Completed a story with 12+ turns',
    tier: 'explorer',
    icon: '\u{1F3C3}', // 🏃
  },
  imagination_unleashed: {
    id: 'imagination_unleashed',
    name: 'Imagination Unleashed',
    description: 'Used custom input 5 times',
    tier: 'explorer',
    icon: '\u{1F4AD}', // 💭
  },

  // =============================================
  // VETERAN TIER - Medium (for returning players)
  // =============================================
  five_stories_finished: {
    id: 'five_stories_finished',
    name: 'Story Collector',
    description: 'Finished 5 complete adventures',
    tier: 'veteran',
    icon: '\u{1F48E}', // 💎
  },
  ten_stories_started: {
    id: 'ten_stories_started',
    name: 'Adventurer',
    description: 'Started 10 different stories',
    tier: 'veteran',
    icon: '\u{2694}', // ⚔️
  },
  century_club: {
    id: 'century_club',
    name: 'Century Club',
    description: 'Made 100 choices total',
    tier: 'veteran',
    icon: '\u{1F4AF}', // 💯
  },
  storyteller_supreme: {
    id: 'storyteller_supreme',
    name: 'Storyteller Supreme',
    description: 'Started 25 different stories',
    tier: 'veteran',
    icon: '\u{1F451}', // 👑
  },
  completionist: {
    id: 'completionist',
    name: 'Completionist',
    description: 'Finished 10 complete stories',
    tier: 'veteran',
    icon: '\u{2705}', // ✅
  },
  age_master: {
    id: 'age_master',
    name: 'Age Master',
    description: 'Played stories at all 4 reading levels',
    tier: 'veteran',
    icon: '\u{1F393}', // 🎓
  },
  prolific_writer: {
    id: 'prolific_writer',
    name: 'Prolific Writer',
    description: 'Used custom input 10 times',
    tier: 'veteran',
    icon: '\u{1F4DD}', // 📝
  },

  // =============================================
  // SPECIAL TIER - Fun extras & unique challenges
  // =============================================
  quick_reader: {
    id: 'quick_reader',
    name: 'Speed Reader',
    description: 'Made 5 choices in a single story',
    tier: 'special',
    icon: '\u{26A1}', // ⚡
  },
  creative_writer: {
    id: 'creative_writer',
    name: 'Wordsmith',
    description: 'Used custom input 3 times',
    tier: 'special',
    icon: '\u{1F58B}', // 🖋️
  },
  bookworm: {
    id: 'bookworm',
    name: 'Bookworm',
    description: 'Made 50 choices total',
    tier: 'special',
    icon: '\u{1F41B}', // 🐛
  },
  curious_cat: {
    id: 'curious_cat',
    name: 'Curious Cat',
    description: 'Checked your achievements 10 times',
    tier: 'special',
    icon: '\u{1F431}', // 🐱
  },
  halfway_hero: {
    id: 'halfway_hero',
    name: 'Halfway Hero',
    description: 'Unlocked half of all achievements',
    tier: 'special',
    icon: '\u{1F9B8}', // 🦸
  },
  dedicated_fan: {
    id: 'dedicated_fan',
    name: 'Dedicated Fan',
    description: 'Finished 15 complete stories',
    tier: 'special',
    icon: '\u{2B50}', // ⭐
  },
  chapter_champion: {
    id: 'chapter_champion',
    name: 'Chapter Champion',
    description: 'Completed stories of 3 different lengths',
    tier: 'special',
    icon: '\u{1F4D1}', // 📑
  },
  tale_weaver: {
    id: 'tale_weaver',
    name: 'Tale Weaver',
    description: 'Started 50 different stories',
    tier: 'special',
    icon: '\u{1F9F5}', // 🧵
  },
};

// Tier colors matching the storybook theme
export const TIER_COLORS: Record<AchievementTier, TierColors> = {
  beginner: {
    border: '#c5a572',
    background: '#f5e6c8',
    glow: 'rgba(197, 165, 114, 0.4)',
  },
  explorer: {
    border: '#1d4d3e',
    background: '#d4e8dc',
    glow: 'rgba(29, 77, 62, 0.4)',
  },
  veteran: {
    border: '#6b1d2b',
    background: '#f9e8e1',
    glow: 'rgba(107, 29, 43, 0.4)',
  },
  special: {
    border: '#e4b94f',
    background: '#faf3da',
    glow: 'rgba(228, 185, 79, 0.5)',
  },
};

export const TIER_NAMES: Record<AchievementTier, string> = {
  beginner: 'Beginner',
  explorer: 'Explorer',
  veteran: 'Veteran',
  special: 'Special',
};

export const TIER_ORDER: AchievementTier[] = ['beginner', 'explorer', 'veteran', 'special'];

export const TOTAL_ACHIEVEMENTS = Object.keys(ACHIEVEMENTS).length;
