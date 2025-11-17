/**
 * ChoiceButton Component
 * Displays a choice button for the player to click
 * Optimization 2.1: Enhanced with Framer Motion micro-interactions
 * Optimization 2.3: Typography & Visual Hierarchy
 * Optimization 2.4: Dark Mode Support
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
        boxShadow: "0 8px 16px rgba(0, 0, 0, 0.3)"
      } : undefined}
      whileTap={!disabled ? { scale: 0.95 } : undefined}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 17
      }}
      className={`
        w-full p-3 md:p-4 text-left rounded-xl border-4 transition-all duration-250
        ${disabled
          ? 'bg-gray-200 dark:bg-dark-bg-tertiary border-gray-300 dark:border-dark-border-secondary text-gray-500 dark:text-dark-text-tertiary cursor-not-allowed'
          : 'bg-gradient-to-r from-primary-400 to-primary-500 dark:from-primary-500 dark:to-primary-600 border-primary-600 dark:border-primary-700 text-white hover:from-primary-500 hover:to-primary-600 dark:hover:from-primary-600 dark:hover:to-primary-700 shadow-card dark:shadow-card-dark'
        }
        font-body text-base md:text-lg font-bold
      `}
      aria-label={`Choice: ${choice.text}`}
    >
      {choice.text}
    </motion.button>
  );
};

export default ChoiceButton;
