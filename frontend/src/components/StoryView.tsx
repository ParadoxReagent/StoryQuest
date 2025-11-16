/**
 * StoryView Component
 * Displays the current scene and player choices
 */

import React from 'react';
import type { StoryResponse } from '../types/api';
import ChoiceButton from './ChoiceButton';
import CustomInput from './CustomInput';

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
                <p className="font-kid text-primary-100">
                  Turn {story.metadata.turns + 1}
                </p>
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
        <div className="prose prose-lg max-w-none">
          <p className="font-kid text-xl leading-relaxed text-gray-800 whitespace-pre-wrap">
            {isStreaming ? streamingText : story.current_scene.text}
            {isStreaming && (
              <span className="inline-block w-2 h-6 ml-1 bg-primary-600 animate-pulse"></span>
            )}
          </p>
        </div>
      </div>

      {/* Loading Indicator */}
      {disabled && (
        <div className="bg-yellow-50 border-4 border-yellow-300 rounded-2xl p-6 shadow-lg">
          <div className="flex items-center justify-center gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-yellow-500 border-t-transparent"></div>
            <p className="font-kid text-xl font-bold text-yellow-700">
              Creating your story... ✨
            </p>
          </div>
        </div>
      )}

      {/* Choices */}
      {!disabled && !isStreaming && (
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
