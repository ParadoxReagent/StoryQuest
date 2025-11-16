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
  // Throttle streaming text for smooth, consistent animation
  // This prevents flickering on fast LLMs by controlling visual display speed
  const throttledText = useThrottledText(streamingText, isStreaming, {
    charsPerFrame: 3,  // Reveal 3 characters per frame
    frameDelay: 20,    // Update every 20ms (50fps) = ~150 chars/second
  });

  // Use the current scene text as the display text, with smooth transitions
  // Show old scene text until new streaming text arrives
  const displayText = isStreaming && throttledText ? throttledText : story.current_scene.text;
  // Only show cursor when we have a reasonable amount of text streaming
  const showCursor = isStreaming && throttledText.length > 10;

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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Story Header */}
      {story.metadata && (
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white p-6 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-4xl">{themeEmoji}</span>
              <div>
                <h2 className="font-kid text-2xl font-bold">
                  {story.metadata.theme.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h2>
                {turnLabel && (
                  <p className="font-kid text-primary-100">
                    {turnLabel}
                  </p>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="font-kid text-sm text-primary-100">Session ID</p>
              <p className="font-kid text-xs text-primary-200 font-mono">
                {story.session_id.substring(0, 8)}...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Current Scene */}
      <div className="bg-white p-8 rounded-2xl border-4 border-primary-300 shadow-xl">
        <div className="prose prose-lg max-w-none story-text-container">
          <div className="min-h-[6rem]">
            <p className="font-kid text-xl leading-relaxed text-gray-800 whitespace-pre-wrap">
              {displayText}
              {/* Blinking cursor during streaming */}
              {showCursor && (
                <span className="inline-block w-0.5 h-6 bg-primary-500 ml-0.5 animate-pulse align-middle" />
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Loading Indicator - Only show during initial load, not during streaming */}
      {disabled && !story.current_scene.text && !isFinished && (
        <div className="bg-yellow-50 border-4 border-yellow-300 rounded-2xl p-6 shadow-lg story-scene-enter">
          <div className="flex items-center justify-center gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-yellow-500 border-t-transparent"></div>
            <p className="font-kid text-xl font-bold text-yellow-700">
              Creating your story... ✨
            </p>
          </div>
        </div>
      )}

      {/* Ending message */}
      {isFinished && (
        <div className="bg-gradient-to-r from-primary-100 to-primary-200 border-4 border-primary-300 rounded-2xl p-6 shadow-lg text-center">
          <p className="font-kid text-xl text-primary-800">
            The adventure has wrapped up with a happy ending! Start a new story to explore another world.
          </p>
        </div>
      )}

      {/* Choices */}
      {!disabled && !isStreaming && !isFinished && (
        <div className="space-y-4">
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
  );
};

export default StoryView;
