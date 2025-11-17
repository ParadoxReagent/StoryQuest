/**
 * ThemeCardSkeleton Component
 * Skeleton loading state for theme cards
 * Optimization 2.1: Advanced Micro-Interactions
 * Optimization 2.4: Dark Mode Support
 */

import React from 'react';
import { motion } from 'framer-motion';

export const ThemeCardSkeleton: React.FC = () => {
  return (
    <motion.div
      className="p-6 rounded-xl border-4 border-gray-200 dark:border-dark-border-secondary bg-white dark:bg-dark-bg-tertiary transition-colors duration-250"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Emoji skeleton */}
      <motion.div
        className="w-16 h-16 rounded-lg mb-3"
        animate={{
          backgroundColor: ['#e5e7eb', '#f3f4f6', '#e5e7eb'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Title skeleton */}
      <motion.div
        className="h-7 rounded-md mb-2"
        animate={{
          backgroundColor: ['#e5e7eb', '#f3f4f6', '#e5e7eb'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.1
        }}
      />

      {/* Description skeleton - 2 lines */}
      <motion.div
        className="h-4 rounded-md mb-1"
        animate={{
          backgroundColor: ['#e5e7eb', '#f3f4f6', '#e5e7eb'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.2
        }}
      />
      <motion.div
        className="h-4 rounded-md w-3/4"
        animate={{
          backgroundColor: ['#e5e7eb', '#f3f4f6', '#e5e7eb'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.3
        }}
      />
    </motion.div>
  );
};

export default ThemeCardSkeleton;
