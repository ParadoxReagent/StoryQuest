/**
 * TypingIndicator Component
 * Optimization 3.1: Shows while LLM is generating content
 */

import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center justify-center gap-2 p-6">
      <div className="flex gap-1">
        <span
          className="w-2 h-2 bg-primary-500 dark:bg-primary-400 rounded-full animate-bounce transition-colors duration-250"
          style={{ animationDelay: '0ms' }}
        />
        <span
          className="w-2 h-2 bg-primary-500 dark:bg-primary-400 rounded-full animate-bounce transition-colors duration-250"
          style={{ animationDelay: '100ms' }}
        />
        <span
          className="w-2 h-2 bg-primary-500 dark:bg-primary-400 rounded-full animate-bounce transition-colors duration-250"
          style={{ animationDelay: '200ms' }}
        />
      </div>
      <span className="ml-2 font-body text-gray-600 dark:text-dark-text-secondary transition-colors duration-250">
        The storyteller is thinking...
      </span>
    </div>
  );
};

export default TypingIndicator;
