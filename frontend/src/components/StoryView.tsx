/**
 * StoryView Component
 * Displays the current scene and player choices
 */

import React from 'react';
import type { StoryResponse } from '../types/api';
import ChoiceButton from './ChoiceButton';
import CustomInput from './CustomInput';
import { useThrottledText } from '../hooks/useThrottledText';

interface Choice {
  choice_id: string;
  text: string;
}

interface StoryViewProps {
  story: StoryResponse;
  onChoiceClick: (choice: Choice) => void;
  onCustomInput: (input: string) => void;
  disabled?: boolean;
  streamingText?: string;
  isStreaming?: boolean;
}

export const StoryView: React.FC<StoryViewProps> = ({
  story,
  onChoiceClick,
  onCustomInput,
  disabled = false,
  streamingText = '',
  isStreaming = false,
}) => {
  // Throttle streaming text for smooth, natural fade-in
  // Slower rate creates a pleasant, readable typing effect
  const throttledText = useThrottledText(streamingText, {
    charsPerFrame: 2,  // Reveal 2 characters per frame
    frameDelay: 30,    // Update every 30ms (33fps) = ~66 chars/second
  });

  // Use the current scene text as the display text, with smooth transitions
  // Always prefer throttled text if it exists (even after streaming stops)
  // This ensures smooth completion of the reveal animation
  const displayText = throttledText || story.current_scene.text;

  const isFinished = story.metadata?.is_finished;
  const maxTurns = story.metadata?.max_turns;
  const themeEmojis: Record<string, string> = {
    space_adventure: '🚀',
    magical_forest: '🌲',
    underwater_quest: '🌊',
    dinosaur_discovery: '🦕',
    castle_quest: '🏰',
    robot_city: '🤖',
  };

  const themeEmoji = story.metadata?.theme
    ? themeEmojis[story.metadata.theme] || '✨'
    : '✨';

  const turnLabel = story.metadata
    ? isFinished
      ? `Completed in ${story.metadata.turns} turn${story.metadata.turns === 1 ? '' : 's'}`
      : `Turn ${story.metadata.turns + 1}${maxTurns ? ` / ${maxTurns}` : ''}`
    : '';

  return (
    <div className="flex flex-col h-full lg:h-auto">
      {/* Story Content Area (scrollable on mobile) */}
      <div className="flex-1 lg:flex-none overflow-y-auto lg:overflow-visible pb-4 lg:pb-0">
        <div className="space-y-4 md:space-y-6 max-w-4xl mx-auto">
          {/* Story Header */}
          {story.metadata && (
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white p-4 md:p-6 rounded-2xl shadow-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 md:gap-3">
                  <span className="text-3xl md:text-4xl">{themeEmoji}</span>
                  <div>
                    <h2 className="font-kid text-lg md:text-2xl font-bold">
                      {story.metadata.theme.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h2>
                    {turnLabel && (
                      <p className="font-kid text-sm md:text-base text-primary-100">
                        {turnLabel}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-right hidden sm:block">
                  <p className="font-kid text-sm text-primary-100">Session ID</p>
                  <p className="font-kid text-xs text-primary-200 font-mono">
                    {story.session_id.substring(0, 8)}...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Current Scene - Compact Display */}
          <div className="bg-white p-4 md:p-6 lg:p-8 rounded-2xl border-4 border-primary-300 shadow-xl">
            <div className="prose prose-lg max-w-none story-text-container">
              {/* Max height for story text with scrolling - Optimization 1.2 */}
              <div className="min-h-[4rem] max-h-[60vh] overflow-y-auto">
                {/* Responsive font sizes - Optimization 1.2 */}
                <p className="font-kid text-lg sm:text-xl md:text-2xl leading-normal text-gray-800 whitespace-pre-wrap story-text-smooth">
                  {displayText}
                </p>
              </div>
            </div>
          </div>

          {/* Loading Indicator - Only show during initial load, not during streaming */}
          {disabled && !story.current_scene.text && !isFinished && (
            <div className="bg-yellow-50 border-4 border-yellow-300 rounded-2xl p-4 md:p-6 shadow-lg story-scene-enter">
              <div className="flex items-center justify-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 md:h-8 md:w-8 border-4 border-yellow-500 border-t-transparent"></div>
                <p className="font-kid text-lg md:text-xl font-bold text-yellow-700">
                  Creating your story... ✨
                </p>
              </div>
            </div>
          )}

          {/* Ending message */}
          {isFinished && (
            <div className="bg-gradient-to-r from-primary-100 to-primary-200 border-4 border-primary-300 rounded-2xl p-4 md:p-6 shadow-lg text-center">
              <p className="font-kid text-lg md:text-xl text-primary-800">
                The adventure has wrapped up with a happy ending! Start a new story to explore another world.
              </p>
            </div>
          )}

          {/* Choices for Desktop - Inline */}
          {!disabled && !isStreaming && !isFinished && (
            <div className="hidden lg:block space-y-4">
              <h3 className="font-kid text-2xl font-bold text-center text-primary-700">
                What would you like to do? 🤔
              </h3>

              <div className="space-y-3">
                {story.choices.map((choice) => (
                  <ChoiceButton
                    key={choice.choice_id}
                    choice={choice}
                    onClick={() => onChoiceClick(choice)}
                    disabled={disabled}
                  />
                ))}
              </div>

              {/* Custom Input */}
              <div className="pt-2">
                <CustomInput
                  onSubmit={onCustomInput}
                  disabled={disabled}
                  maxLength={200}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Fixed Choice Bar - Mobile/Tablet - Optimization 1.1 */}
      {!disabled && !isStreaming && !isFinished && (
        <div className="lg:hidden fixed inset-x-0 bottom-0 z-30 border-t-4 border-primary-300 bg-white/95 backdrop-blur-sm shadow-2xl">
          <div className="max-w-4xl mx-auto p-4 space-y-3">
            <h3 className="font-kid text-lg sm:text-xl font-bold text-center text-primary-700">
              What would you like to do? 🤔
            </h3>

            <div className="space-y-2">
              {story.choices.map((choice) => (
                <ChoiceButton
                  key={choice.choice_id}
                  choice={choice}
                  onClick={() => onChoiceClick(choice)}
                  disabled={disabled}
                />
              ))}
            </div>

            {/* Custom Input */}
            <div>
              <CustomInput
                onSubmit={onCustomInput}
                disabled={disabled}
                maxLength={200}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryView;
