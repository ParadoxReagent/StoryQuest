/**
 * LoadingStoryBook Component
 * Animated story book opening effect for loading states
 * Part of Optimization 2.1: Advanced Micro-Interactions
 */

import React from 'react';
import { motion } from 'framer-motion';

interface LoadingStoryBookProps {
  message?: string;
}

export const LoadingStoryBook: React.FC<LoadingStoryBookProps> = ({
  message = 'Creating your story...'
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-8 md:py-12">
      {/* Animated Story Book */}
      <div className="relative w-32 h-32 md:w-40 md:h-40 mb-6">
        {/* Book Cover - Left Page */}
        <motion.div
          className="absolute left-0 top-0 w-16 md:w-20 h-32 md:h-40 bg-gradient-to-r from-primary-500 to-primary-600 rounded-l-lg shadow-lg origin-right"
          initial={{ rotateY: 0 }}
          animate={{ rotateY: -25 }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
          style={{
            transformStyle: 'preserve-3d',
            backfaceVisibility: 'hidden'
          }}
        >
          <div className="flex items-center justify-center h-full text-4xl md:text-5xl">
            📖
          </div>
        </motion.div>

        {/* Book Cover - Right Page */}
        <motion.div
          className="absolute right-0 top-0 w-16 md:w-20 h-32 md:h-40 bg-gradient-to-l from-primary-500 to-primary-600 rounded-r-lg shadow-lg origin-left"
          initial={{ rotateY: 0 }}
          animate={{ rotateY: 25 }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
          style={{
            transformStyle: 'preserve-3d',
            backfaceVisibility: 'hidden'
          }}
        />

        {/* Sparkles */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-2xl"
            initial={{
              opacity: 0,
              scale: 0,
              x: 64,
              y: 64
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
              x: [64, 64 + (i - 1) * 40, 64 + (i - 1) * 60],
              y: [64, 20 + i * 10, 0]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.3,
              ease: "easeOut"
            }}
          >
            ✨
          </motion.div>
        ))}
      </div>

      {/* Loading Message */}
      <motion.p
        className="font-kid text-lg md:text-xl font-bold text-primary-700 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {message}
      </motion.p>

      {/* Animated Dots */}
      <div className="flex gap-1 mt-2">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="text-primary-500 text-xl font-bold"
            animate={{ opacity: [0, 1, 0] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut"
            }}
          >
            .
          </motion.span>
        ))}
      </div>
    </div>
  );
};

export default LoadingStoryBook;
