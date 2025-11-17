/**
 * CustomInput Component
 * Allows players to type their own response
 * Optimization 2.3: Typography & Visual Hierarchy
 * Optimization 2.4: Dark Mode Support
 */

import React, { useState } from 'react';

interface CustomInputProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  maxLength?: number;
}

export const CustomInput: React.FC<CustomInputProps> = ({
  onSubmit,
  disabled = false,
  maxLength = 200
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSubmit(inputValue.trim());
      setInputValue('');
      setIsExpanded(false);
    }
  };

  const remainingChars = maxLength - inputValue.length;
  const isValid = inputValue.trim().length > 0 && inputValue.length <= maxLength;

  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        disabled={disabled}
        className={`
          w-full p-3 md:p-4 rounded-xl border-4 border-dashed transition-all duration-250
          ${disabled
            ? 'bg-gray-100 dark:bg-dark-bg-tertiary border-gray-300 dark:border-dark-border-secondary text-gray-500 dark:text-dark-text-tertiary cursor-not-allowed'
            : 'bg-white dark:bg-dark-bg-tertiary border-primary-300 dark:border-dark-border-primary text-primary-700 dark:text-primary-400 hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-dark-bg-secondary'
          }
          font-body text-base md:text-lg font-bold
        `}
        aria-label="Type your own response"
      >
        <span className="flex items-center justify-center">
          <span className="mr-2 md:mr-3 text-xl md:text-2xl">✏️</span>
          <span>Or type your own idea!</span>
        </span>
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="bg-white dark:bg-dark-bg-secondary p-3 md:p-4 rounded-xl border-4 border-primary-400 dark:border-primary-600 shadow-card dark:shadow-card-dark transition-colors duration-250">
        <label htmlFor="custom-input" className="block mb-2 font-heading text-base md:text-lg font-bold text-primary-700 dark:text-primary-400">
          What would you like to do? ✏️
        </label>
        <textarea
          id="custom-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={disabled}
          maxLength={maxLength}
          placeholder="Type your own creative idea here..."
          className="w-full p-2 md:p-3 border-2 border-primary-200 dark:border-dark-border-secondary rounded-lg font-body text-base md:text-lg bg-white dark:bg-dark-bg-tertiary text-gray-800 dark:text-dark-text-primary placeholder-gray-400 dark:placeholder-dark-text-tertiary resize-none focus:outline-none focus:border-primary-500 dark:focus:border-primary-400 transition-colors duration-250"
          rows={3}
          autoFocus
          aria-label="Custom input text area"
        />
        <div className="flex items-center justify-between mt-2">
          <span className={`text-xs md:text-sm font-body ${remainingChars < 20 ? 'text-red-500 dark:text-red-400 font-bold' : 'text-gray-500 dark:text-dark-text-tertiary'}`}>
            {remainingChars} left
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setInputValue('');
                setIsExpanded(false);
              }}
              className="px-3 md:px-4 py-1.5 md:py-2 text-sm md:text-base rounded-lg border-2 border-gray-300 dark:border-dark-border-secondary bg-white dark:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary font-body font-bold hover:bg-gray-100 dark:hover:bg-dark-bg-secondary transition-all duration-250"
              aria-label="Cancel custom input"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!isValid}
              className={`
                px-4 md:px-6 py-1.5 md:py-2 text-sm md:text-base rounded-lg font-body font-bold transition-all duration-250
                ${isValid
                  ? 'bg-gradient-to-r from-green-400 to-green-500 dark:from-green-500 dark:to-green-600 text-white hover:from-green-500 hover:to-green-600 dark:hover:from-green-600 dark:hover:to-green-700 shadow-md hover:shadow-lg dark:shadow-card-dark'
                  : 'bg-gray-300 dark:bg-dark-bg-tertiary text-gray-500 dark:text-dark-text-tertiary cursor-not-allowed'
                }
              `}
              aria-label="Submit custom input"
            >
              Send! 🚀
            </button>
          </div>
        </div>
      </div>
    </form>
  );
};

export default CustomInput;
