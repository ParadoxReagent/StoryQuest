/**
 * StoryHistory Component
 * Displays a collapsible history of the story so far
 * Optimization 2.3: Typography & Visual Hierarchy
 * Optimization 2.4: Dark Mode Support
 */

import React, { useState } from 'react';

interface Turn {
  scene_text: string;
  player_choice?: string;
  custom_input?: string;
  turn_number: number;
}

interface StoryHistoryProps {
  turns: Turn[];
}

export const StoryHistory: React.FC<StoryHistoryProps> = ({ turns }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (turns.length === 0) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full bg-white dark:bg-dark-bg-secondary p-4 rounded-xl border-4 border-gray-300 dark:border-dark-border-primary hover:border-primary-400 dark:hover:border-primary-500 transition-all duration-250 shadow-card dark:shadow-card-dark hover:shadow-card-hover dark:hover:shadow-card-hover-dark"
        aria-label={isExpanded ? "Hide story history" : "Show story history"}
        aria-expanded={isExpanded}
      >
        <div className="flex items-center justify-between">
          <span className="font-heading text-lg font-bold text-gray-700 dark:text-dark-text-primary flex items-center gap-2 transition-colors duration-250">
            <span className="text-2xl">📖</span>
            Story So Far ({turns.length} turn{turns.length !== 1 ? 's' : ''})
          </span>
          <span className="text-3xl text-primary-500 dark:text-primary-400 transition-all duration-250" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
            ⌄
          </span>
        </div>
      </button>

      {isExpanded && (
        <div className="mt-4 bg-white dark:bg-dark-bg-secondary p-6 rounded-xl border-4 border-gray-300 dark:border-dark-border-primary shadow-card dark:shadow-card-dark space-y-4 max-h-96 overflow-y-auto transition-colors duration-250">
          {turns.map((turn) => (
            <div
              key={turn.turn_number}
              className="border-l-4 border-primary-400 dark:border-primary-500 pl-4 py-2"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="font-body text-sm font-bold text-primary-600 dark:text-primary-400">
                  Turn {turn.turn_number}
                </span>
                {turn.turn_number === 0 && (
                  <span className="text-xs font-body bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">
                    Start
                  </span>
                )}
              </div>

              <p className="font-body text-base text-gray-700 dark:text-dark-text-secondary mb-2">
                {turn.scene_text}
              </p>

              {(turn.player_choice || turn.custom_input) && (
                <div className="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg mt-2 transition-colors duration-250">
                  <p className="font-body text-sm font-bold text-primary-700 dark:text-primary-400 mb-1">
                    You chose:
                  </p>
                  <p className="font-body text-sm text-primary-600 dark:text-primary-300 italic">
                    {turn.custom_input || turn.player_choice}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StoryHistory;
