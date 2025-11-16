/**
 * ThemeSelection Component
 * Allows the player to start a new story with a chosen theme
 * Optimization 2.1: Enhanced with animations and skeleton screens
 * Optimization 2.2: Enhanced Theme Selection UI
 * Optimization 2.3: Typography & Visual Hierarchy
 * Optimization 2.4: Dark Mode Support
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { generateThemes } from '../services/api';
import ThemeCardSkeleton from './ThemeCardSkeleton';
import type { ThemeOption } from '../types/api';

interface ThemeSelectionProps {
  onStart: (playerName: string, ageRange: string, theme: string) => void;
  disabled?: boolean;
}

const ageRanges = [
  { value: '6-8', label: '6-8 years old' },
  { value: '9-12', label: '9-12 years old' },
];

// Helper to convert Tailwind gradient classes to inline CSS
const getGradientStyle = (colorClasses: string): React.CSSProperties => {
  // Map of Tailwind color names to hex values
  const colorMap: Record<string, string> = {
    'indigo-400': '#818cf8',
    'purple-500': '#a855f7',
    'green-400': '#4ade80',
    'emerald-500': '#10b981',
    'cyan-400': '#22d3ee',
    'blue-500': '#3b82f6',
    'orange-400': '#fb923c',
    'red-500': '#ef4444',
    'yellow-400': '#facc15',
    'amber-500': '#f59e0b',
    'pink-400': '#f472b6',
    'rose-500': '#f43f5e',
    'teal-400': '#2dd4bf',
    'violet-400': '#a78bfa',
    'fuchsia-500': '#d946ef',
  };

  // Parse "from-color-400 to-color-500" format
  const parts = colorClasses.split(' ');
  const fromColor = parts[0]?.replace('from-', '');
  const toColor = parts[1]?.replace('to-', '');

  const startColor = colorMap[fromColor] || '#6366f1';
  const endColor = colorMap[toColor] || '#8b5cf6';

  return {
    background: `linear-gradient(to bottom right, ${startColor}, ${endColor})`,
  };
};

export const ThemeSelection: React.FC<ThemeSelectionProps> = ({ onStart, disabled = false }) => {
  const [playerName, setPlayerName] = useState('');
  const [ageRange, setAgeRange] = useState('6-8');
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null);
  const [themes, setThemes] = useState<ThemeOption[]>([]);
  const [loadingThemes, setLoadingThemes] = useState(true);
  const [themesError, setThemesError] = useState<string | null>(null);

  // Fetch themes when component mounts or age range changes
  useEffect(() => {
    const fetchThemes = async () => {
      setLoadingThemes(true);
      setThemesError(null);
      setSelectedTheme(null); // Reset selection when themes change

      try {
        const response = await generateThemes({ age_range: ageRange });
        setThemes(response.themes);
      } catch (error) {
        console.error('Failed to generate themes:', error);
        setThemesError('Failed to load themes. Please try again.');
      } finally {
        setLoadingThemes(false);
      }
    };

    fetchThemes();
  }, [ageRange]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (playerName.trim() && selectedTheme) {
      onStart(playerName.trim(), ageRange, selectedTheme);
    }
  };

  const isValid = playerName.trim().length > 0 && selectedTheme !== null;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Optimization 2.3: Enhanced Typography with font-heading */}
      <div className="text-center mb-8">
        <motion.h1
          className="text-5xl md:text-6xl font-heading font-bold text-primary-600 dark:text-primary-400 mb-4 transition-colors duration-250"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          StoryQuest ✨
        </motion.h1>
        <motion.p
          className="text-xl md:text-2xl font-body text-gray-700 dark:text-dark-text-secondary transition-colors duration-250"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          Let's begin your amazing adventure!
        </motion.p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Optimization 2.2 & 2.4: Enhanced Player Name Input with dark mode */}
        <motion.div
          className="bg-white dark:bg-dark-bg-secondary p-6 rounded-2xl border-4 border-primary-300 dark:border-dark-border-primary shadow-card dark:shadow-card-dark transition-colors duration-250"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <label htmlFor="player-name" className="block mb-3 font-heading text-xl font-bold text-primary-700 dark:text-primary-400 flex items-center gap-2">
            <span className="text-2xl">👤</span>
            What's your name, adventurer?
          </label>
          <input
            type="text"
            id="player-name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            disabled={disabled}
            placeholder="Enter your name..."
            maxLength={100}
            className="w-full p-4 border-4 border-primary-200 dark:border-dark-border-secondary rounded-xl font-body text-xl bg-white dark:bg-dark-bg-tertiary text-gray-800 dark:text-dark-text-primary placeholder-gray-400 dark:placeholder-dark-text-tertiary focus:outline-none focus:border-primary-500 dark:focus:border-primary-400 disabled:bg-gray-100 dark:disabled:bg-dark-bg-primary disabled:cursor-not-allowed transition-colors duration-250"
            aria-label="Player name input"
          />
        </motion.div>

        {/* Optimization 2.2 & 2.4: Enhanced Age Range Selection with dark mode */}
        <motion.div
          className="bg-white dark:bg-dark-bg-secondary p-6 rounded-2xl border-4 border-primary-300 dark:border-dark-border-primary shadow-card dark:shadow-card-dark transition-colors duration-250"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        >
          <label className="block mb-4 font-heading text-xl font-bold text-primary-700 dark:text-primary-400 flex items-center gap-2">
            <span className="text-2xl">🎂</span>
            How old are you?
          </label>
          <div className="flex gap-4">
            {ageRanges.map((range) => (
              <motion.button
                key={range.value}
                type="button"
                onClick={() => setAgeRange(range.value)}
                disabled={disabled}
                whileHover={!disabled ? { scale: 1.03 } : undefined}
                whileTap={!disabled ? { scale: 0.97 } : undefined}
                className={`
                  flex-1 p-4 rounded-xl border-4 font-body text-lg font-bold transition-all duration-250
                  ${ageRange === range.value
                    ? 'bg-primary-500 dark:bg-primary-600 border-primary-600 dark:border-primary-700 text-white scale-105 shadow-card-hover dark:shadow-card-hover-dark'
                    : 'bg-white dark:bg-dark-bg-tertiary border-primary-300 dark:border-dark-border-secondary text-primary-700 dark:text-dark-text-primary hover:border-primary-500 dark:hover:border-primary-400 hover:scale-102'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                aria-label={`Select age range: ${range.label}`}
                aria-pressed={ageRange === range.value}
              >
                {range.label}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Optimization 2.2: Enhanced Theme Selection with better visual hierarchy */}
        <motion.div
          className="bg-white dark:bg-dark-bg-secondary p-6 rounded-2xl border-4 border-primary-300 dark:border-dark-border-primary shadow-card dark:shadow-card-dark transition-colors duration-250"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          <label className="block mb-4 font-heading text-xl font-bold text-primary-700 dark:text-primary-400 flex items-center gap-2">
            <span className="text-2xl">🎭</span>
            Choose your adventure!
          </label>

          {/* Loading state with skeleton screens - Optimization 2.1 */}
          {loadingThemes && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <ThemeCardSkeleton key={i} />
              ))}
            </div>
          )}

          {/* Error state with dark mode support */}
          {themesError && !loadingThemes && (
            <div className="text-center py-8">
              <p className="font-body text-lg text-red-600 dark:text-red-400 mb-4">{themesError}</p>
              <motion.button
                type="button"
                onClick={() => {
                  setLoadingThemes(true);
                  setThemesError(null);
                  generateThemes({ age_range: ageRange })
                    .then(response => setThemes(response.themes))
                    .catch(error => {
                      console.error('Failed to generate themes:', error);
                      setThemesError('Failed to load themes. Please try again.');
                    })
                    .finally(() => setLoadingThemes(false));
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-6 py-3 bg-primary-500 dark:bg-primary-600 text-white font-body text-lg rounded-xl hover:bg-primary-600 dark:hover:bg-primary-700 transition-all duration-250 shadow-lg"
              >
                Try Again
              </motion.button>
            </div>
          )}

          {/* Optimization 2.2: Enhanced themes grid with improved cards */}
          {!loadingThemes && !themesError && themes.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {themes.map((theme, i) => (
                <motion.button
                  key={theme.id}
                  type="button"
                  onClick={() => setSelectedTheme(theme.id)}
                  disabled={disabled}
                  style={selectedTheme === theme.id ? getGradientStyle(theme.color) : undefined}
                  className={`
                    p-6 rounded-xl border-4 transition-all duration-250 text-left
                    ${selectedTheme === theme.id
                      ? 'border-white dark:border-white/80 text-white shadow-card-hover dark:shadow-card-hover-dark'
                      : 'bg-white dark:bg-dark-bg-tertiary border-gray-300 dark:border-dark-border-secondary hover:border-primary-400 dark:hover:border-primary-500 shadow-card dark:shadow-card-dark'
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: selectedTheme === theme.id ? 1.05 : 1 }}
                  transition={{ delay: i * 0.1, duration: 0.3 }}
                  whileHover={!disabled ? { scale: selectedTheme === theme.id ? 1.05 : 1.02 } : undefined}
                  whileTap={!disabled ? { scale: 0.98 } : undefined}
                  aria-label={`Select theme: ${theme.name}`}
                  aria-pressed={selectedTheme === theme.id}
                >
                  <div className="text-5xl mb-3">{theme.emoji}</div>
                  <div className={`font-heading text-xl font-bold mb-2 ${selectedTheme === theme.id ? 'text-white' : 'text-gray-800 dark:text-dark-text-primary'}`}>
                    {theme.name}
                  </div>
                  <div className={`font-body text-sm leading-relaxed ${selectedTheme === theme.id ? 'text-white/90' : 'text-gray-600 dark:text-dark-text-secondary'}`}>
                    {theme.description}
                  </div>
                </motion.button>
              ))}
            </div>
          )}
        </motion.div>

        {/* Optimization 2.2 & 2.3: Enhanced Start Button with better typography */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.4 }}
        >
          <motion.button
            type="submit"
            disabled={!isValid || disabled}
            whileHover={isValid && !disabled ? {
              scale: 1.1,
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.3)"
            } : undefined}
            whileTap={isValid && !disabled ? { scale: 0.95 } : undefined}
            transition={{
              type: "spring",
              stiffness: 400,
              damping: 17
            }}
            className={`
              px-12 py-6 rounded-2xl border-4 font-heading text-2xl font-bold transition-all duration-250
              ${isValid && !disabled
                ? 'bg-gradient-to-r from-green-400 to-green-500 dark:from-green-500 dark:to-green-600 border-green-600 dark:border-green-700 text-white hover:from-green-500 hover:to-green-600 dark:hover:from-green-600 dark:hover:to-green-700 shadow-card-hover dark:shadow-card-hover-dark'
                : 'bg-gray-300 dark:bg-dark-bg-tertiary border-gray-400 dark:border-dark-border-secondary text-gray-500 dark:text-dark-text-tertiary cursor-not-allowed'
              }
            `}
            aria-label="Start adventure"
          >
            🎉 Start My Adventure! 🎉
          </motion.button>
        </motion.div>
      </form>
    </div>
  );
};

export default ThemeSelection;
