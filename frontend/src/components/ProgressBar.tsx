/**
 * ProgressBar Component
 * Optimization 3.1: Visual turn counter showing progress toward max turns
 */

import React from 'react';

interface ProgressBarProps {
  currentTurn: number;
  maxTurns: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ currentTurn, maxTurns }) => {
  const progress = (currentTurn / maxTurns) * 100;

  return (
    <div className="w-full space-y-2">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 dark:bg-dark-border-primary rounded-full h-2 overflow-hidden transition-colors duration-250">
        <div
          className="bg-gradient-to-r from-blue-500 to-purple-500 dark:from-blue-400 dark:to-purple-400 h-2 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Turn counter text */}
      <p className="text-sm text-gray-600 dark:text-dark-text-secondary text-center font-body transition-colors duration-250">
        Turn {currentTurn} of {maxTurns}
      </p>
    </div>
  );
};

export default ProgressBar;
