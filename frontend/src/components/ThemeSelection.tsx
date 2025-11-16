/**
 * ThemeSelection Component
 * Allows the player to start a new story with a chosen theme
 */

import React, { useState } from 'react';

interface ThemeSelectionProps {
  onStart: (playerName: string, ageRange: string, theme: string) => void;
  disabled?: boolean;
}

interface Theme {
  id: string;
  name: string;
  description: string;
  emoji: string;
  color: string;
}

const themes: Theme[] = [
  {
    id: 'space_adventure',
    name: 'Space Adventure',
    description: 'Explore planets, stars, and meet friendly aliens!',
    emoji: '🚀',
    color: 'from-indigo-400 to-purple-500',
  },
  {
    id: 'magical_forest',
    name: 'Magical Forest',
    description: 'Journey through an enchanted forest with magical creatures!',
    emoji: '🌲',
    color: 'from-green-400 to-emerald-500',
  },
  {
    id: 'underwater_quest',
    name: 'Underwater Quest',
    description: 'Dive deep and discover hidden treasures!',
    emoji: '🌊',
    color: 'from-cyan-400 to-blue-500',
  },
  {
    id: 'dinosaur_discovery',
    name: 'Dinosaur Discovery',
    description: 'Travel back in time to meet friendly dinosaurs!',
    emoji: '🦕',
    color: 'from-orange-400 to-red-500',
  },
  {
    id: 'castle_quest',
    name: 'Castle Quest',
    description: 'Explore a grand castle with knights and dragons!',
    emoji: '🏰',
    color: 'from-yellow-400 to-amber-500',
  },
  {
    id: 'robot_city',
    name: 'Robot City',
    description: 'Visit a futuristic city with helpful robots!',
    emoji: '🤖',
    color: 'from-gray-400 to-slate-500',
  },
];

const ageRanges = [
  { value: '6-8', label: '6-8 years old' },
  { value: '9-12', label: '9-12 years old' },
];

export const ThemeSelection: React.FC<ThemeSelectionProps> = ({ onStart, disabled = false }) => {
  const [playerName, setPlayerName] = useState('');
  const [ageRange, setAgeRange] = useState('6-8');
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null);

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
            What's your name, adventurer? 🌟
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
            How old are you? 🎂
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
            Choose your adventure! 🎮
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {themes.map((theme) => (
              <button
                key={theme.id}
                type="button"
                onClick={() => setSelectedTheme(theme.id)}
                disabled={disabled}
                className={`
                  p-6 rounded-xl border-4 transition-all duration-200 text-left
                  ${selectedTheme === theme.id
                    ? `bg-gradient-to-br ${theme.color} border-white text-white scale-105 shadow-xl`
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
