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
      className="fixed top-4 right-4 z-50 p-3 rounded-full border-4 border-white/30 bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-all duration-250 shadow-lg"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{ rotate: isDark ? 180 : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="text-3xl"
      >
        {isDark ? '🌙' : '☀️'}
      </motion.div>
    </motion.button>
  );
};

export default ThemeToggle;
