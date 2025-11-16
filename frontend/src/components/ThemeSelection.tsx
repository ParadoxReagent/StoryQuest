/**
 * ThemeSelection Component
 * Allows the player to start a new story with a chosen theme
 */

import React, { useState, useEffect } from 'react';
import { generateThemes } from '../services/api';
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
      <div className="text-center mb-8">
        <h1 className="text-6xl font-kid font-bold text-primary-600 mb-4">
          StoryQuest ✨
        </h1>
        <p className="text-2xl font-kid text-gray-700">
          Let's begin your amazing adventure!
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Player Name Input */}
        <div className="bg-white p-6 rounded-2xl border-4 border-primary-300 shadow-lg">
          <label htmlFor="player-name" className="block mb-2 font-kid text-xl font-bold text-primary-700">
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
            className="w-full p-4 border-4 border-primary-200 rounded-xl font-kid text-xl focus:outline-none focus:border-primary-500 disabled:bg-gray-100"
            aria-label="Player name input"
          />
        </div>

        {/* Age Range Selection */}
        <div className="bg-white p-6 rounded-2xl border-4 border-primary-300 shadow-lg">
          <label className="block mb-4 font-kid text-xl font-bold text-primary-700">
            How old are you?
          </label>
          <div className="flex gap-4">
            {ageRanges.map((range) => (
              <button
                key={range.value}
                type="button"
                onClick={() => setAgeRange(range.value)}
                disabled={disabled}
                className={`
                  flex-1 p-4 rounded-xl border-4 font-kid text-lg font-bold transition-all duration-200
                  ${ageRange === range.value
                    ? 'bg-primary-500 border-primary-600 text-white scale-105 shadow-lg'
                    : 'bg-white border-primary-300 text-primary-700 hover:border-primary-500 hover:scale-102'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                aria-label={`Select age range: ${range.label}`}
                aria-pressed={ageRange === range.value}
              >
                {range.label}
              </button>
            ))}
          </div>
        </div>

        {/* Theme Selection */}
        <div className="bg-white p-6 rounded-2xl border-4 border-primary-300 shadow-lg">
          <label className="block mb-4 font-kid text-xl font-bold text-primary-700">
            Choose your adventure!
          </label>

          {/* Loading state */}
          {loadingThemes && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-500 mb-4"></div>
              <p className="font-kid text-lg text-gray-600">Creating magical themes just for you...</p>
            </div>
          )}

          {/* Error state */}
          {themesError && !loadingThemes && (
            <div className="text-center py-8">
              <p className="font-kid text-lg text-red-600 mb-4">{themesError}</p>
              <button
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
                className="px-6 py-3 bg-primary-500 text-white font-kid text-lg rounded-xl hover:bg-primary-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Themes grid */}
          {!loadingThemes && !themesError && themes.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {themes.map((theme) => (
                <button
                  key={theme.id}
                  type="button"
                  onClick={() => setSelectedTheme(theme.id)}
                  disabled={disabled}
                  style={selectedTheme === theme.id ? getGradientStyle(theme.color) : undefined}
                  className={`
                    p-6 rounded-xl border-4 transition-all duration-200 text-left
                    ${selectedTheme === theme.id
                      ? 'border-white text-white scale-105 shadow-xl'
                      : 'bg-white border-gray-300 hover:border-primary-400 hover:scale-102 shadow-md'
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                  aria-label={`Select theme: ${theme.name}`}
                  aria-pressed={selectedTheme === theme.id}
                >
                  <div className="text-5xl mb-3">{theme.emoji}</div>
                  <div className={`font-kid text-xl font-bold mb-2 ${selectedTheme === theme.id ? 'text-white' : 'text-gray-800'}`}>
                    {theme.name}
                  </div>
                  <div className={`font-kid text-sm ${selectedTheme === theme.id ? 'text-white/90' : 'text-gray-600'}`}>
                    {theme.description}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Start Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={!isValid || disabled}
            className={`
              px-12 py-6 rounded-2xl border-4 font-kid text-2xl font-bold transition-all duration-200
              ${isValid && !disabled
                ? 'bg-gradient-to-r from-green-400 to-green-500 border-green-600 text-white hover:from-green-500 hover:to-green-600 hover:scale-110 active:scale-95 shadow-xl hover:shadow-2xl'
                : 'bg-gray-300 border-gray-400 text-gray-500 cursor-not-allowed'
              }
            `}
            aria-label="Start adventure"
          >
            🎉 Start My Adventure! 🎉
          </button>
        </div>
      </form>
    </div>
  );
};

export default ThemeSelection;
