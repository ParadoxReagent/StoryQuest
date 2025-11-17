/**
 * Theme Toggle Component
 * Optimization 2.4: Dark Mode Support
 * A toggle button for switching between light and dark modes
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { mode, toggleMode } = useTheme();
  const isDark = mode === 'dark';

  return (
    <motion.button
      onClick={toggleMode}
      className="px-4 py-2 md:px-6 md:py-3 rounded-xl border-4 border-white dark:border-white/20 bg-white/20 dark:bg-white/10 hover:bg-white/30 dark:hover:bg-white/20 text-white font-body font-bold backdrop-blur-sm transition-all duration-200 shadow-lg text-sm md:text-base flex items-center justify-center"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <motion.span
        initial={false}
        animate={{ rotate: isDark ? 180 : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="inline-block"
      >
        {isDark ? '🌙' : '☀️'}
      </motion.span>
    </motion.button>
  );
};

export default ThemeToggle;
