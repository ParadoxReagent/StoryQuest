/**
 * StoryView Component
 * Displays the current scene and player choices
 * Optimization 2.1: Enhanced with scene transition animations
 * Optimization 2.3: Typography & Visual Hierarchy
 * Optimization 2.4: Dark Mode Support
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import type { StoryResponse } from '../types/api';
import ChoiceButton from './ChoiceButton';
import CustomInput from './CustomInput';
import LoadingStoryBook from './LoadingStoryBook';
import ProgressBar from './ProgressBar';
import TypingIndicator from './TypingIndicator';
import { useThrottledText } from '../hooks/useThrottledText';
import { TTSPlayer, initialTTSState, type TTSPlaybackState } from '../services/tts';

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

  // Track whether choices should be visible based on streaming progress
  const [showChoices, setShowChoices] = useState(false);

  // TTS state management
  const [ttsState, setTtsState] = useState<TTSPlaybackState>(initialTTSState);
  const ttsPlayerRef = useRef<TTSPlayer | null>(null);

  // Initialize TTS player
  useEffect(() => {
    ttsPlayerRef.current = new TTSPlayer(setTtsState);
    return () => {
      ttsPlayerRef.current?.destroy();
    };
  }, []);

  // Stop TTS when scene changes
  useEffect(() => {
    ttsPlayerRef.current?.stop();
  }, [story.current_scene.scene_id]);

  // Handle TTS button click
  const handleTTSClick = useCallback(() => {
    if (!ttsPlayerRef.current) return;
    const textToSpeak = story.current_scene.text;
    if (textToSpeak) {
      ttsPlayerRef.current.toggle(textToSpeak);
    }
  }, [story.current_scene.text]);

  // Show choices after a 2-second delay from when streaming starts
  useEffect(() => {
    if (disabled) {
      // Reset when disabled (new turn starting)
      setShowChoices(false);
      return;
    }

    if (isStreaming) {
      // Start a 3.5-second timer when streaming begins
      const timer = setTimeout(() => {
        setShowChoices(true);
      }, 3500);

      return () => clearTimeout(timer);
    } else if (!isStreaming && !disabled) {
      // Always show choices when not streaming and not disabled
      setShowChoices(true);
    }
  }, [isStreaming, disabled]);

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
          {/* Story Header - Optimization 2.3 & 2.4: Enhanced typography and dark mode */}
          {story.metadata && (
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 text-white p-4 md:p-6 rounded-2xl shadow-card dark:shadow-card-dark transition-colors duration-250">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 md:gap-3">
                  <span className="text-3xl md:text-4xl">{themeEmoji}</span>
                  <div>
                    <h2 className="font-heading text-lg md:text-2xl font-bold">
                      {story.metadata.theme.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h2>
                    {turnLabel && (
                      <p className="font-body text-sm md:text-base text-primary-100 dark:text-primary-200">
                        {turnLabel}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {/* TTS Narration Button */}
                  <button
                    onClick={handleTTSClick}
                    disabled={ttsState.isLoading || isStreaming || !story.current_scene.text}
                    className={`
                      p-2 rounded-full transition-all duration-200
                      ${ttsState.isPlaying
                        ? 'bg-white/30 text-white'
                        : 'bg-white/10 hover:bg-white/20 text-white/80 hover:text-white'
                      }
                      disabled:opacity-50 disabled:cursor-not-allowed
                    `}
                    title={ttsState.isPlaying ? 'Pause narration' : 'Play narration'}
                    aria-label={ttsState.isPlaying ? 'Pause narration' : 'Play narration'}
                  >
                    {ttsState.isLoading ? (
                      <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : ttsState.isPlaying ? (
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                      </svg>
                    )}
                  </button>
                  <div className="text-right hidden sm:block">
                    <p className="font-body text-sm text-primary-100 dark:text-primary-200">Session ID</p>
                    <p className="font-body text-xs text-primary-200 dark:text-primary-300 font-mono">
                      {story.session_id.substring(0, 8)}...
                    </p>
                  </div>
                </div>
              </div>

              {/* Progress Bar - Optimization 3.1 */}
              {!isFinished && maxTurns && (
                <div className="opacity-90">
                  <ProgressBar
                    currentTurn={story.metadata.turns + 1}
                    maxTurns={maxTurns}
                  />
                </div>
              )}
            </div>
          )}

          {/* Current Scene - Optimization 2.3 & 2.4: Enhanced with dark mode */}
          <div className="bg-white dark:bg-dark-bg-secondary p-4 md:p-6 lg:p-8 rounded-2xl border-4 border-primary-300 dark:border-dark-border-primary shadow-xl dark:shadow-card-dark transition-colors duration-250">
            <div className="prose prose-lg max-w-none story-text-container">
              {/* Max height for story text with scrolling - Optimization 1.2 */}
              <div className="min-h-[4rem] max-h-[60vh] overflow-y-auto">
                {/* Optimization 2.3: Enhanced typography with font-body */}
                <p className="font-body text-lg sm:text-xl md:text-2xl leading-normal text-gray-800 dark:text-dark-text-primary whitespace-pre-wrap story-text-smooth transition-colors duration-250">
                  {displayText}
                </p>
              </div>
            </div>
          </div>

          {/* Loading Indicator - Optimization 2.1 & 2.4: With dark mode */}
          {disabled && !story.current_scene.text && !isFinished && (
            <div className="bg-gradient-to-br from-yellow-50 to-primary-50 dark:from-yellow-900/20 dark:to-primary-900/20 border-4 border-primary-300 dark:border-primary-600 rounded-2xl p-4 md:p-6 shadow-xl dark:shadow-card-dark transition-colors duration-250">
              <LoadingStoryBook message="Creating your story... ✨" />
            </div>
          )}

          {/* Typing Indicator - Optimization 3.1: Show while LLM is generating */}
          {isStreaming && (
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-4 border-primary-300 dark:border-primary-600 rounded-2xl shadow-xl dark:shadow-card-dark transition-colors duration-250">
              <TypingIndicator />
            </div>
          )}

          {/* Ending message - Optimization 2.3 & 2.4 */}
          {isFinished && (
            <div className="bg-gradient-to-r from-primary-100 to-primary-200 dark:from-primary-900/40 dark:to-primary-800/40 border-4 border-primary-300 dark:border-primary-600 rounded-2xl p-4 md:p-6 shadow-lg dark:shadow-card-dark text-center transition-colors duration-250">
              <p className="font-body text-lg md:text-xl text-primary-800 dark:text-primary-200">
                The adventure has wrapped up with a happy ending! Start a new story to explore another world.
              </p>
            </div>
          )}

          {/* Choices for Desktop - Inline - Optimization 2.3 & 2.4 */}
          {showChoices && !isFinished && (
            <div className="hidden lg:block space-y-4">
              <motion.h3
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="font-heading text-2xl font-bold text-center text-primary-700 dark:text-primary-400 transition-colors duration-250"
              >
                What would you like to do? 🤔
              </motion.h3>

              <div className="space-y-3">
                {story.choices.map((choice, index) => (
                  <motion.div
                    key={choice.choice_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      duration: 0.8,
                      delay: index * 0.25,
                      ease: "easeOut"
                    }}
                  >
                    <ChoiceButton
                      choice={choice}
                      onClick={() => onChoiceClick(choice)}
                      disabled={disabled}
                    />
                  </motion.div>
                ))}
              </div>

              {/* Custom Input */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.8,
                  delay: story.choices.length * 0.25,
                  ease: "easeOut"
                }}
                className="pt-2"
              >
                <CustomInput
                  onSubmit={onCustomInput}
                  disabled={disabled}
                  maxLength={200}
                />
              </motion.div>
            </div>
          )}
        </div>
      </div>

      {/* Fixed Choice Bar - Mobile/Tablet - Optimization 1.1, 2.3 & 2.4 */}
      {showChoices && !isFinished && (
        <div className="lg:hidden fixed inset-x-0 bottom-0 z-30 border-t-4 border-primary-300 dark:border-dark-border-primary bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-sm shadow-2xl dark:shadow-card-dark transition-colors duration-250">
          <div className="max-w-4xl mx-auto p-4 space-y-3">
            <motion.h3
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="font-heading text-lg sm:text-xl font-bold text-center text-primary-700 dark:text-primary-400 transition-colors duration-250"
            >
              What would you like to do? 🤔
            </motion.h3>

            <div className="space-y-2">
              {story.choices.map((choice, index) => (
                <motion.div
                  key={choice.choice_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    duration: 0.8,
                    delay: index * 0.25,
                    ease: "easeOut"
                  }}
                >
                  <ChoiceButton
                    choice={choice}
                    onClick={() => onChoiceClick(choice)}
                    disabled={disabled}
                  />
                </motion.div>
              ))}
            </div>

            {/* Custom Input */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.8,
                delay: story.choices.length * 0.25,
                ease: "easeOut"
              }}
            >
              <CustomInput
                onSubmit={onCustomInput}
                disabled={disabled}
                maxLength={200}
              />
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryView;
