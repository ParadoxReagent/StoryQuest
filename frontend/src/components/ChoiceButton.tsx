/**
 * ChoiceButton Component
 * Displays a choice button for the player to click
 * Enhanced with Framer Motion micro-interactions (Optimization 2.1)
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { Choice } from '../types/api';

interface ChoiceButtonProps {
  choice: Choice;
  onClick: () => void;
  disabled?: boolean;
}

export const ChoiceButton: React.FC<ChoiceButtonProps> = ({ choice, onClick, disabled = false }) => {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? {
        scale: 1.05,
        boxShadow: "0 8px 16px rgba(0, 0, 0, 0.2)"
      } : undefined}
      whileTap={!disabled ? { scale: 0.95 } : undefined}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 17
      }}
      className={`
        w-full p-3 md:p-4 text-left rounded-xl border-4 transition-colors duration-200
        ${disabled
          ? 'bg-gray-200 border-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-primary-400 to-primary-500 border-primary-600 text-white hover:from-primary-500 hover:to-primary-600 shadow-lg'
        }
        font-kid text-base md:text-lg font-bold
      `}
      aria-label={`Choice: ${choice.text}`}
    >
      {choice.text}
    </motion.button>
  );
};

export default ChoiceButton;
