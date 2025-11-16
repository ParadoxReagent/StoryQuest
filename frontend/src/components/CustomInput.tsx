/**
 * CustomInput Component
 * Allows players to type their own response
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
          w-full p-4 rounded-xl border-4 border-dashed transition-all duration-200
          ${disabled
            ? 'bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-white border-primary-300 text-primary-700 hover:border-primary-500 hover:bg-primary-50'
          }
          font-kid text-lg font-bold
        `}
        aria-label="Type your own response"
      >
        <span className="flex items-center justify-center">
          <span className="mr-3 text-2xl">✏️</span>
          <span>Or type your own idea!</span>
        </span>
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="bg-white p-4 rounded-xl border-4 border-primary-400 shadow-lg">
        <label htmlFor="custom-input" className="block mb-2 font-kid text-lg font-bold text-primary-700">
          What would you like to do? ✏️
        </label>
        <textarea
          id="custom-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={disabled}
          maxLength={maxLength}
          placeholder="Type your own creative idea here..."
          className="w-full p-3 border-2 border-primary-200 rounded-lg font-kid text-lg resize-none focus:outline-none focus:border-primary-500"
          rows={3}
          autoFocus
          aria-label="Custom input text area"
        />
        <div className="flex items-center justify-between mt-2">
          <span className={`text-sm font-kid ${remainingChars < 20 ? 'text-red-500 font-bold' : 'text-gray-500'}`}>
            {remainingChars} characters left
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setInputValue('');
                setIsExpanded(false);
              }}
              className="px-4 py-2 rounded-lg border-2 border-gray-300 bg-white text-gray-700 font-kid font-bold hover:bg-gray-100 transition-colors"
              aria-label="Cancel custom input"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!isValid}
              className={`
                px-6 py-2 rounded-lg font-kid font-bold transition-all duration-200
                ${isValid
                  ? 'bg-gradient-to-r from-green-400 to-green-500 text-white hover:from-green-500 hover:to-green-600 shadow-md hover:shadow-lg'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
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
