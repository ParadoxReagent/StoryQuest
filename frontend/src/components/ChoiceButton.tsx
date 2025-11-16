/**
 * ChoiceButton Component
 * Displays a choice button for the player to click
 */

import React from 'react';
import type { Choice } from '../types/api';

interface ChoiceButtonProps {
  choice: Choice;
  onClick: () => void;
  disabled?: boolean;
}

export const ChoiceButton: React.FC<ChoiceButtonProps> = ({ choice, onClick, disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        w-full p-4 text-left rounded-xl border-4 transition-all duration-200
        ${disabled
          ? 'bg-gray-200 border-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-primary-400 to-primary-500 border-primary-600 text-white hover:from-primary-500 hover:to-primary-600 hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl'
        }
        font-kid text-lg font-bold
      `}
      aria-label={`Choice: ${choice.text}`}
    >
      {choice.text}
    </button>
  );
};

export default ChoiceButton;
