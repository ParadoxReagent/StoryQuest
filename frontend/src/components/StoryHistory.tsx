/**
 * StoryHistory Component
 * Displays a collapsible history of the story so far
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
        className="w-full bg-white p-4 rounded-xl border-4 border-gray-300 hover:border-primary-400 transition-all duration-200 shadow-md hover:shadow-lg"
        aria-label={isExpanded ? "Hide story history" : "Show story history"}
        aria-expanded={isExpanded}
      >
        <div className="flex items-center justify-between">
          <span className="font-kid text-lg font-bold text-gray-700 flex items-center gap-2">
            <span className="text-2xl">📖</span>
            Story So Far ({turns.length} turn{turns.length !== 1 ? 's' : ''})
          </span>
          <span className="text-3xl text-primary-500 transition-transform duration-200" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
            ⌄
          </span>
        </div>
      </button>

      {isExpanded && (
        <div className="mt-4 bg-white p-6 rounded-xl border-4 border-gray-300 shadow-lg space-y-4 max-h-96 overflow-y-auto">
          {turns.map((turn) => (
            <div
              key={turn.turn_number}
              className="border-l-4 border-primary-400 pl-4 py-2"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="font-kid text-sm font-bold text-primary-600">
                  Turn {turn.turn_number}
                </span>
                {turn.turn_number === 0 && (
                  <span className="text-xs font-kid bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    Start
                  </span>
                )}
              </div>

              <p className="font-kid text-base text-gray-700 mb-2">
                {turn.scene_text}
              </p>

              {(turn.player_choice || turn.custom_input) && (
                <div className="bg-primary-50 p-3 rounded-lg mt-2">
                  <p className="font-kid text-sm font-bold text-primary-700 mb-1">
                    You chose:
                  </p>
                  <p className="font-kid text-sm text-primary-600 italic">
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
