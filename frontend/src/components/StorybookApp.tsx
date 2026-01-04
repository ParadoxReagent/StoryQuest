/**
 * StorybookApp - Interactive Storybook Interface
 * A magical, immersive choose-your-own-adventure experience
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast, Toaster } from 'sonner';
import { generateThemes, startStoryStream, continueStoryStream } from '../services/api';
import { TTSPlayer, initialTTSState, type TTSPlaybackState } from '../services/tts';
import type { StoryResponse, ThemeOption } from '../types/api';

// ============================================
// TYPES
// ============================================
type BookState = 'closed' | 'opening' | 'theme-selection' | 'page-turning' | 'playing' | 'loading';

interface Turn {
  scene_text: string;
  player_choice?: string;
  custom_input?: string;
  turn_number: number;
}

// ============================================
// SPARKLE COMPONENT (CSS-only for GPU performance)
// ============================================
const Sparkles = ({ count = 20 }: { count?: number }) => {
  // Memoize sparkle positions - only recalculate if count changes
  const sparkles = useMemo(() =>
    Array.from({ length: count }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: Math.random() * 4,
      duration: 3 + Math.random() * 2,
      size: 2 + Math.random() * 4,
    })),
  [count]);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {sparkles.map((sparkle) => (
        <div
          key={sparkle.id}
          className="sparkle-particle absolute rounded-full"
          style={{
            left: sparkle.left,
            top: sparkle.top,
            width: sparkle.size,
            height: sparkle.size,
            animationDelay: `${sparkle.delay}s`,
            animationDuration: `${sparkle.duration}s`,
          }}
        />
      ))}
    </div>
  );
};

// ============================================
// CORNER DECORATION COMPONENT
// ============================================
const CornerDecoration = ({ position }: { position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' }) => {
  const rotations = {
    'top-left': 0,
    'top-right': 90,
    'bottom-left': -90,
    'bottom-right': 180,
  };

  const positions = {
    'top-left': { top: 0, left: 0 },
    'top-right': { top: 0, right: 0 },
    'bottom-left': { bottom: 0, left: 0 },
    'bottom-right': { bottom: 0, right: 0 },
  };

  return (
    <div
      className="absolute w-16 h-16 md:w-20 md:h-20"
      style={{
        ...positions[position],
        transform: `rotate(${rotations[position]}deg)`,
      }}
    >
      <svg viewBox="0 0 80 80" className="w-full h-full">
        <defs>
          <linearGradient id={`gold-${position}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#e4b94f" />
            <stop offset="50%" stopColor="#c5a572" />
            <stop offset="100%" stopColor="#926d3d" />
          </linearGradient>
        </defs>
        <path
          d="M0 0 L80 0 L80 15 Q40 15 15 40 L15 80 L0 80 Z"
          fill={`url(#gold-${position})`}
        />
        <path
          d="M5 5 L70 5 L70 12 Q38 12 12 38 L12 70 L5 70 Z"
          fill="#6b1d2b"
        />
        {/* Decorative flourish */}
        <circle cx="25" cy="25" r="3" fill={`url(#gold-${position})`} />
        <path
          d="M20 35 Q25 30 30 35"
          stroke={`url(#gold-${position})`}
          strokeWidth="1.5"
          fill="none"
        />
      </svg>
    </div>
  );
};

// ============================================
// ORNATE BORDER COMPONENT
// ============================================
const OrnateBorder = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <div className={`relative ${className}`}>
    <div className="absolute inset-0 border-2 border-storybook-gold-500 rounded-lg" />
    <div className="absolute -top-1 -left-1 w-4 h-4 border-l-2 border-t-2 border-storybook-gold-400 rounded-tl" />
    <div className="absolute -top-1 -right-1 w-4 h-4 border-r-2 border-t-2 border-storybook-gold-400 rounded-tr" />
    <div className="absolute -bottom-1 -left-1 w-4 h-4 border-l-2 border-b-2 border-storybook-gold-400 rounded-bl" />
    <div className="absolute -bottom-1 -right-1 w-4 h-4 border-r-2 border-b-2 border-storybook-gold-400 rounded-br" />
    {children}
  </div>
);

// ============================================
// AGE SLIDER HELPER
// ============================================
interface ReadingLevel {
  label: string;
  description: string;
}

const getReadingLevel = (age: number): ReadingLevel => {
  if (age <= 7) return { label: 'Early Reader', description: 'Wonder & Friendship' };
  if (age <= 10) return { label: 'Middle Reader', description: 'Action & Bravery' };
  if (age <= 13) return { label: 'Tween', description: 'Moral Dilemmas' };
  return { label: 'Young Adult', description: 'Complex Themes' };
};

const getAgeRangeFromAge = (age: number): string => {
  if (age <= 7) return '5-7';
  if (age <= 10) return '8-10';
  if (age <= 13) return '11-13';
  return '14-18';
};

// ============================================
// CLOSED BOOK COMPONENT
// ============================================
interface ClosedBookProps {
  playerName: string;
  setPlayerName: (name: string) => void;
  age: number;
  setAge: (age: number) => void;
  onOpen: () => void;
  isValid: boolean;
}

const ClosedBook = ({ playerName, setPlayerName, age, setAge, onOpen, isValid }: ClosedBookProps) => {
  const readingLevel = getReadingLevel(age);
  return (
    <motion.div
      className="relative w-full max-w-md mx-auto"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
    >
      {/* Book Cover */}
      <div className="book-cover aspect-[3/4] p-6 md:p-10 flex flex-col items-center justify-between">
        {/* Corner Decorations */}
        <CornerDecoration position="top-left" />
        <CornerDecoration position="top-right" />
        <CornerDecoration position="bottom-left" />
        <CornerDecoration position="bottom-right" />

        {/* Top Section - Title */}
        <div className="text-center mt-8 md:mt-12 relative z-10">
          <motion.h1
            className="font-storybook-title text-3xl md:text-5xl embossed tracking-wider"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            StoryQuest
          </motion.h1>
          <motion.div
            className="mt-2 h-0.5 w-32 md:w-48 mx-auto bg-gradient-to-r from-transparent via-storybook-gold-500 to-transparent"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          />
          <motion.p
            className="font-storybook-fancy text-sm md:text-base text-storybook-gold-400 mt-2 italic"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            An Interactive Adventure
          </motion.p>
        </div>

        {/* Middle Section - Name Input (Embossed Plate) */}
        <motion.div
          className="w-full max-w-xs relative z-10"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          <div className="embossed-border rounded-lg p-4 md:p-6">
            <label className="block text-center mb-3">
              <span className="font-storybook-heading text-xs md:text-sm text-storybook-gold-400 uppercase tracking-widest">
                This book belongs to
              </span>
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
              maxLength={50}
              className="embossed-input w-full text-lg md:text-xl"
              aria-label="Enter your name"
            />
          </div>
        </motion.div>

        {/* Bottom Section - Age Slider */}
        <motion.div
          className="mb-6 md:mb-10 relative z-10 w-full max-w-xs mx-auto px-4"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.6 }}
        >
          {/* Reading Level Display */}
          <div className="text-center mb-4">
            <motion.div
              key={readingLevel.label}
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-block"
            >
              <span className="font-storybook-heading text-xs md:text-sm text-storybook-gold-400 uppercase tracking-widest">
                Age {age}
              </span>
              <span className="mx-2 text-storybook-gold-600">•</span>
              <span className="font-storybook-fancy text-sm md:text-base text-storybook-gold-300 italic">
                {readingLevel.label}
              </span>
            </motion.div>
            <motion.p
              key={readingLevel.description}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-storybook-body text-xs text-storybook-parchment-400 mt-1"
            >
              {readingLevel.description}
            </motion.p>
          </div>

          {/* Custom Slider */}
          <div className="age-slider-container">
            <input
              type="range"
              min={5}
              max={18}
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value, 10))}
              className="age-slider"
              aria-label={`Select age: ${age} years old, ${readingLevel.label}`}
            />
            {/* Slider Track Decorations */}
            <div className="age-slider-markers">
              <span className="text-storybook-gold-600 font-storybook-body text-xs">5</span>
              <span className="text-storybook-gold-600 font-storybook-body text-xs">18</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Open Book Button */}
      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2">
        <motion.button
          onClick={onOpen}
          disabled={!isValid}
          className={`
            px-8 py-3 rounded-full
            font-storybook-heading text-sm md:text-base uppercase tracking-widest
            transition-all duration-300
            ${isValid
              ? 'bg-gradient-to-r from-storybook-gold-400 via-storybook-gold-500 to-storybook-gold-600 text-storybook-leather-900 shadow-gold-glow hover:shadow-book-hover cursor-pointer'
              : 'bg-storybook-ink-600 text-storybook-ink-400 cursor-not-allowed'
            }
          `}
          whileHover={isValid ? { scale: 1.05, y: -2 } : undefined}
          whileTap={isValid ? { scale: 0.98 } : undefined}
          aria-label="Begin your adventure"
        >
          Begin Adventure
        </motion.button>
      </div>
    </motion.div>
  );
};

// ============================================
// OPEN BOOK COMPONENT
// ============================================
interface OpenBookProps {
  leftContent: React.ReactNode;
  rightContent: React.ReactNode;
  onNewStory?: () => void;
  showNewStoryButton?: boolean;
}

const OpenBook = ({ leftContent, rightContent, onNewStory, showNewStoryButton }: OpenBookProps) => {
  return (
    <motion.div
      className="w-full max-w-6xl mx-auto"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* New Story Button */}
      {showNewStoryButton && onNewStory && (
        <motion.button
          onClick={onNewStory}
          className="absolute top-4 right-4 z-50 px-4 py-2 rounded-lg bg-storybook-leather-800/80 border border-storybook-gold-500/50 text-storybook-gold-400 font-storybook-heading text-sm hover:bg-storybook-leather-700 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          New Story
        </motion.button>
      )}

      {/* Desktop: Side by side */}
      <div className="hidden md:flex book-spread rounded-lg overflow-hidden shadow-book">
        {/* Left Page */}
        <div className="book-page left-page flex-1 min-h-[500px] lg:min-h-[600px] p-6 lg:p-10">
          <div className="page-edge" />
          <div className="relative h-full overflow-y-auto storybook-scroll pl-4">
            {leftContent}
          </div>
        </div>

        {/* Spine */}
        <div className="book-spine" />

        {/* Right Page */}
        <div className="book-page right-page flex-1 min-h-[500px] lg:min-h-[600px] p-6 lg:p-10">
          <div className="page-edge" />
          <div className="relative h-full overflow-y-auto storybook-scroll pr-4">
            {rightContent}
          </div>
        </div>
      </div>

      {/* Mobile: Stacked pages */}
      <div className="md:hidden flex flex-col gap-4">
        {/* Story/Left Content */}
        <div className="book-page rounded-lg min-h-[300px] p-6">
          <div className="h-full overflow-y-auto storybook-scroll">
            {leftContent}
          </div>
        </div>

        {/* Choices/Right Content */}
        <div className="book-page rounded-lg min-h-[200px] p-6">
          <div className="h-full overflow-y-auto storybook-scroll">
            {rightContent}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// THEME SELECTION CONTENT
// ============================================
interface ThemeSelectionContentProps {
  themes: ThemeOption[];
  selectedTheme: string | null;
  onSelectTheme: (themeId: string) => void;
  onStartStory: () => void;
  isLoading: boolean;
  playerName: string;
}

const ThemeSelectionContent = ({
  themes,
  selectedTheme,
  onSelectTheme,
  onStartStory,
  isLoading,
  playerName,
}: ThemeSelectionContentProps) => {
  // Left page - decorative welcome
  const leftPage = (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="text-6xl md:text-8xl mb-4">
          <span role="img" aria-label="Open book">
            {'\u2728'}
          </span>
        </div>
        <h2 className="font-storybook-title text-2xl md:text-4xl text-storybook-ink-900 mb-4">
          Welcome, {playerName}!
        </h2>
        <div className="w-24 h-0.5 mx-auto bg-gradient-to-r from-transparent via-storybook-gold-500 to-transparent mb-4" />
        <p className="font-storybook-body text-lg md:text-xl text-storybook-ink-700 italic max-w-xs">
          Choose your adventure from the tales within these pages...
        </p>
      </motion.div>

      {/* Decorative illustration */}
      <motion.div
        className="mt-8 opacity-30"
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.3 }}
        transition={{ delay: 0.6 }}
      >
        <svg width="150" height="100" viewBox="0 0 150 100" className="text-storybook-ink-600">
          <path
            d="M20 80 Q75 20 130 80"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
          />
          <circle cx="75" cy="30" r="15" stroke="currentColor" strokeWidth="2" fill="none" />
          <path d="M60 70 L75 55 L90 70" stroke="currentColor" strokeWidth="2" fill="none" />
        </svg>
      </motion.div>
    </div>
  );

  // Right page - theme selection grid
  const rightPage = (
    <div className="h-full flex flex-col">
      <h3 className="font-storybook-heading text-xl md:text-2xl text-storybook-ink-900 text-center mb-6">
        Choose Your Story
      </h3>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="storybook-loading">
            <span />
            <span />
            <span />
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3 md:gap-4 flex-1">
            {themes.map((theme, index) => (
              <motion.button
                key={theme.id}
                onClick={() => onSelectTheme(theme.id)}
                className={`theme-card-storybook text-left ${
                  selectedTheme === theme.id ? 'selected' : ''
                }`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                aria-pressed={selectedTheme === theme.id}
              >
                <div className="text-3xl md:text-4xl mb-2">{theme.emoji}</div>
                <h4 className="font-storybook-heading text-sm md:text-base text-storybook-ink-900 mb-1">
                  {theme.name}
                </h4>
                <p className="font-storybook-body text-xs md:text-sm text-storybook-ink-700 line-clamp-2">
                  {theme.description}
                </p>
              </motion.button>
            ))}
          </div>

          {/* Start Button */}
          <motion.button
            onClick={onStartStory}
            disabled={!selectedTheme}
            className={`
              mt-6 w-full py-3 rounded-lg
              font-storybook-heading text-base md:text-lg uppercase tracking-wider
              transition-all duration-300
              ${selectedTheme
                ? 'bg-storybook-forest-700 text-storybook-gold-300 hover:bg-storybook-forest-600 shadow-lg'
                : 'bg-storybook-parchment-400 text-storybook-ink-400 cursor-not-allowed'
              }
            `}
            whileHover={selectedTheme ? { scale: 1.02 } : undefined}
            whileTap={selectedTheme ? { scale: 0.98 } : undefined}
          >
            Begin This Tale
          </motion.button>
        </>
      )}
    </div>
  );

  return { leftPage, rightPage };
};

// ============================================
// GAMEPLAY VIEW COMPONENT
// ============================================
interface GameplayViewProps {
  story: StoryResponse;
  streamingText: string;
  isStreaming: boolean;
  isLoading: boolean;
  history: Turn[];
  onChoice: (choice: { choice_id: string; text: string }) => void;
  onCustomInput: (input: string) => void;
  onNewStory: () => void;
}

const GameplayView: React.FC<GameplayViewProps> = ({
  story,
  streamingText,
  isStreaming,
  isLoading,
  history,
  onChoice,
  onCustomInput,
  onNewStory,
}) => {
  const [customInput, setCustomInput] = useState('');
  const displayText = isStreaming ? streamingText : story.current_scene.text;
  const isFinished = story.metadata?.is_finished;

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

  const handleCustomSubmit = () => {
    if (customInput.trim()) {
      onCustomInput(customInput.trim());
      setCustomInput('');
    }
  };

  // Left page content - story text
  const leftPageContent = (
    <div className="h-full flex flex-col">
      {/* Chapter indicator with TTS button */}
      <div className="flex items-center justify-between mb-4">
        <div className="w-10" /> {/* Spacer for centering */}
        <div className="text-center">
          <span className="font-storybook-heading text-xs md:text-sm text-storybook-gold-600 uppercase tracking-widest">
            Chapter {(story.metadata?.turns || 0) + 1}
          </span>
          <div className="w-16 h-0.5 mx-auto mt-1 bg-gradient-to-r from-transparent via-storybook-gold-500 to-transparent" />
        </div>
        {/* TTS Button */}
        <button
          onClick={handleTTSClick}
          disabled={ttsState.isLoading || isStreaming || !story.current_scene.text}
          className={`
            w-10 h-10 rounded-full flex items-center justify-center
            transition-all duration-200 border-2
            ${ttsState.isPlaying
              ? 'bg-storybook-forest-700 border-storybook-forest-600 text-storybook-gold-300'
              : 'bg-storybook-parchment-200 border-storybook-gold-400 text-storybook-ink-700 hover:bg-storybook-parchment-300 hover:border-storybook-gold-500'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          title={ttsState.isPlaying ? 'Pause narration' : 'Listen to story'}
          aria-label={ttsState.isPlaying ? 'Pause narration' : 'Listen to story'}
        >
          {ttsState.isLoading ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : ttsState.isPlaying ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          )}
        </button>
      </div>

      {/* Story text */}
      <div className="flex-1 overflow-y-auto storybook-scroll">
        <motion.div
          key={story.current_scene.scene_id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="font-storybook-body text-base md:text-lg lg:text-xl text-storybook-ink-900 leading-relaxed"
        >
          {displayText.split('\n').map((paragraph, i) => (
            <p key={i} className="mb-4 first-letter:text-3xl first-letter:font-storybook-title first-letter:text-storybook-leather-800 first-letter:float-left first-letter:mr-2">
              {paragraph}
            </p>
          ))}
        </motion.div>

        {/* Loading indicator */}
        {isLoading && !isStreaming && (
          <div className="flex justify-center mt-4">
            <div className="storybook-loading">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
      </div>

      {/* Progress indicator */}
      {story.metadata && (
        <div className="mt-4 pt-4 border-t border-storybook-gold-300/30">
          <div className="flex items-center justify-between text-xs text-storybook-ink-600">
            <span className="font-storybook-body">
              Turn {story.metadata.turns} / {story.metadata.max_turns || '?'}
            </span>
            <div className="flex-1 mx-4 h-1 bg-storybook-parchment-400 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-storybook-forest-600 rounded-full"
                initial={{ width: 0 }}
                animate={{
                  width: `${((story.metadata.turns || 0) / (story.metadata.max_turns || 15)) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Right page content - choices
  const rightPageContent = (
    <div className="h-full flex flex-col">
      <h3 className="font-storybook-heading text-lg md:text-xl text-storybook-ink-900 text-center mb-4">
        {isFinished ? 'The End' : 'What will you do?'}
      </h3>

      {isFinished ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-6xl mb-4">
              <span role="img" aria-label="sparkles">
                {'\u2728'}
              </span>
            </div>
            <p className="font-storybook-body text-lg text-storybook-ink-700 italic mb-6">
              And so your adventure comes to an end...
            </p>
            <OrnateBorder className="p-4">
              <p className="font-storybook-fancy text-sm text-storybook-ink-600">
                Thank you for reading, brave adventurer.
                <br />
                May your next tale be even more wondrous!
              </p>
            </OrnateBorder>
          </motion.div>
        </div>
      ) : (
        <>
          {/* Choice buttons */}
          <div className="flex-1 space-y-3">
            {story.choices.map((choice, index) => (
              <motion.button
                key={choice.choice_id}
                onClick={() => onChoice(choice)}
                disabled={isLoading}
                className="storybook-choice w-full text-left disabled:opacity-50 disabled:cursor-not-allowed"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={!isLoading ? { scale: 1.02 } : undefined}
                whileTap={!isLoading ? { scale: 0.98 } : undefined}
              >
                <span className="font-storybook-body text-sm md:text-base">
                  {choice.text}
                </span>
              </motion.button>
            ))}
          </div>

          {/* Custom input */}
          <div className="mt-4 pt-4 border-t border-storybook-gold-300/30">
            <label className="block font-storybook-heading text-xs text-storybook-ink-600 uppercase tracking-wider mb-2">
              Or write your own action...
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCustomSubmit()}
                disabled={isLoading}
                placeholder="What do you do?"
                className="flex-1 px-3 py-2 rounded-lg border-2 border-storybook-gold-400 bg-storybook-parchment-100 font-storybook-body text-sm text-storybook-ink-900 placeholder-storybook-ink-400 focus:outline-none focus:border-storybook-gold-500 disabled:opacity-50"
              />
              <motion.button
                onClick={handleCustomSubmit}
                disabled={isLoading || !customInput.trim()}
                className="px-4 py-2 rounded-lg bg-storybook-forest-700 text-storybook-gold-300 font-storybook-heading text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Go
              </motion.button>
            </div>
          </div>
        </>
      )}

      {/* Story history toggle */}
      {history.length > 1 && (
        <details className="mt-4 pt-4 border-t border-storybook-gold-300/30">
          <summary className="font-storybook-heading text-xs text-storybook-ink-600 uppercase tracking-wider cursor-pointer hover:text-storybook-ink-800">
            Story So Far ({history.length - 1} turns)
          </summary>
          <div className="mt-2 max-h-32 overflow-y-auto storybook-scroll space-y-2">
            {history.slice(0, -1).map((turn, i) => (
              <div key={i} className="text-xs text-storybook-ink-600 border-l-2 border-storybook-gold-400 pl-2">
                <span className="font-bold">Turn {i + 1}:</span>{' '}
                {turn.scene_text.slice(0, 80)}...
                {turn.player_choice && (
                  <span className="italic"> → {turn.player_choice}</span>
                )}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );

  return (
    <OpenBook
      leftContent={leftPageContent}
      rightContent={rightPageContent}
      onNewStory={onNewStory}
      showNewStoryButton
    />
  );
};

// ============================================
// LOADING SCREEN
// ============================================
const LoadingScreen = () => (
  <div className="w-full max-w-4xl mx-auto">
    <div className="book-page rounded-lg min-h-[400px] md:min-h-[500px] p-8 flex flex-col items-center justify-center">
      <motion.div
        className="text-7xl md:text-8xl mb-6"
        animate={{ rotate: [0, 10, -10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <span role="img" aria-label="open book">
          {'\uD83D\uDCD6'}
        </span>
      </motion.div>
      <h2 className="font-storybook-title text-2xl md:text-3xl text-storybook-leather-800 mb-4 text-center">
        Crafting Your Tale...
      </h2>
      <p className="font-storybook-body text-base md:text-lg text-storybook-ink-700 mb-6 text-center">
        The pages are being written just for you
      </p>
      <div className="storybook-loading">
        <span />
        <span />
        <span />
      </div>
    </div>
  </div>
);

// ============================================
// MAIN STORYBOOK APP COMPONENT
// ============================================
export const StorybookApp = () => {
  // State
  const [bookState, setBookState] = useState<BookState>('closed');
  const [playerName, setPlayerName] = useState('');
  const [age, setAge] = useState(8);
  const ageRange = getAgeRangeFromAge(age); // Derived from age for API calls
  const [themes, setThemes] = useState<ThemeOption[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null);
  const [themesLoading, setThemesLoading] = useState(false);
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [history, setHistory] = useState<Turn[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  // Performance: Throttle streaming updates to reduce re-renders
  const streamingBufferRef = useRef('');
  const lastUpdateTimeRef = useRef(0);
  const STREAMING_THROTTLE_MS = 50; // Update UI every 50ms max

  const isNameValid = playerName.trim().length > 0;

  // Fetch themes when opening book
  const fetchThemes = useCallback(async () => {
    setThemesLoading(true);
    try {
      const response = await generateThemes({ age_range: ageRange });
      setThemes(response.themes);
    } catch (error) {
      console.error('Failed to load themes:', error);
      toast.error('Failed to load story themes. Please try again.');
    } finally {
      setThemesLoading(false);
    }
  }, [ageRange]);

  // Handle book opening
  const handleOpenBook = useCallback(() => {
    if (!isNameValid) return;
    setBookState('opening');

    // Fetch themes during animation
    fetchThemes();

    // Transition to theme selection after animation
    setTimeout(() => {
      setBookState('theme-selection');
    }, 1500);
  }, [isNameValid, fetchThemes]);

  // Helper to extract scene text from streaming buffer
  const extractSceneTextFromStream = (buffer: string): string | null => {
    const match = buffer.match(/"scene_text"\s*:\s*"((?:\\.|[^"\\])*)/);
    if (!match) return null;
    try {
      return JSON.parse(`"${match[1]}"`);
    } catch {
      return match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
    }
  };

  // Handle starting the story
  const handleStartStory = useCallback(async () => {
    if (!selectedTheme) return;

    setBookState('page-turning');

    setTimeout(async () => {
      setBookState('loading');
      setIsLoading(true);
      setStreamingText('');
      setIsStreaming(false);

      try {
        const selectedThemeData = themes.find(t => t.id === selectedTheme);
        const themeName = selectedThemeData?.name || selectedTheme;

        let sessionId = '';
        let finalChoices: any[] = [];
        let finalMetadata: any = null;
        let finalSceneText = '';
        let finalStorySummary = '';
        let accumulatedText = '';

        await startStoryStream(
          { player_name: playerName.trim(), age_range: ageRange, theme: themeName },
          {
            onSessionStart: (sid) => {
              sessionId = sid;
              // Don't change state here - wait until we have story data
            },
            onTextChunk: (chunk) => {
              accumulatedText += chunk;
              streamingBufferRef.current = accumulatedText;

              // Throttle UI updates to reduce re-renders
              const now = Date.now();
              if (now - lastUpdateTimeRef.current >= STREAMING_THROTTLE_MS) {
                const sceneText = extractSceneTextFromStream(accumulatedText);
                if (sceneText) {
                  setIsStreaming(true);
                  setStreamingText(sceneText);
                  lastUpdateTimeRef.current = now;
                }
              }
            },
            onComplete: (choices, metadata, sceneText, storySummary) => {
              finalChoices = choices;
              finalMetadata = metadata;
              finalSceneText = sceneText || '';
              finalStorySummary = storySummary || '';
            },
            onError: (errorMsg) => {
              console.error('Story stream error:', errorMsg);
              toast.error(errorMsg);
              setBookState('theme-selection');
            },
          }
        );

        if (finalMetadata && sessionId) {
          const response: StoryResponse = {
            session_id: sessionId,
            current_scene: {
              scene_id: crypto.randomUUID(),
              text: finalSceneText || accumulatedText,
              timestamp: new Date().toISOString(),
            },
            choices: finalChoices.map((c) => ({
              choice_id: c.choice_id,
              text: c.text,
            })),
            story_summary: finalStorySummary || '',
            metadata: finalMetadata,
          };

          setStory(response);
          setHistory([{ scene_text: finalSceneText || accumulatedText, turn_number: 0 }]);
          // Now transition to playing state with the story data ready
          setBookState('playing');
        } else {
          // No valid response - go back to theme selection
          console.error('No valid story response received');
          toast.error('Failed to generate story. Please try again.');
          setBookState('theme-selection');
        }
      } catch (error) {
        console.error('Failed to start story:', error);
        toast.error('Failed to start story. Please try again.');
        setBookState('theme-selection');
      } finally {
        setIsLoading(false);
        setIsStreaming(false);
      }
    }, 800);
  }, [selectedTheme, themes, playerName, ageRange]);

  // Handle choice selection
  const handleChoice = useCallback(async (choice: { choice_id: string; text: string }) => {
    if (!story || story.metadata?.is_finished) return;

    setIsLoading(true);
    setStreamingText('');
    setIsStreaming(false);

    // Update last history entry with the choice made
    setHistory((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        player_choice: choice.text,
      };
      return updated;
    });

    try {
      let finalChoices: any[] = [];
      let finalMetadata: any = null;
      let finalSceneText = '';
      let finalStorySummary = '';
      let accumulatedText = '';

      await continueStoryStream(
        {
          session_id: story.session_id,
          choice_id: choice.choice_id,
          choice_text: choice.text,
          story_summary: story.story_summary,
        },
        {
          onTextChunk: (chunk) => {
            accumulatedText += chunk;
            streamingBufferRef.current = accumulatedText;

            // Throttle UI updates to reduce re-renders
            const now = Date.now();
            if (now - lastUpdateTimeRef.current >= STREAMING_THROTTLE_MS) {
              const sceneText = extractSceneTextFromStream(accumulatedText);
              if (sceneText) {
                setIsStreaming(true);
                setStreamingText(sceneText);
                lastUpdateTimeRef.current = now;
              }
            }
          },
          onComplete: (choices, metadata, sceneText, storySummary) => {
            finalChoices = choices;
            finalMetadata = metadata;
            finalSceneText = sceneText || '';
            finalStorySummary = storySummary || '';
          },
          onError: (errorMsg) => {
            toast.error(errorMsg);
          },
        }
      );

      if (finalMetadata) {
        const response: StoryResponse = {
          session_id: story.session_id,
          current_scene: {
            scene_id: crypto.randomUUID(),
            text: finalSceneText || accumulatedText,
            timestamp: new Date().toISOString(),
          },
          choices: finalChoices.map((c) => ({
            choice_id: c.choice_id,
            text: c.text,
          })),
          story_summary: finalStorySummary || story.story_summary,
          metadata: finalMetadata,
        };

        setStory(response);
        // Add new scene to history
        setHistory((prev) => [...prev, { scene_text: finalSceneText || accumulatedText, turn_number: prev.length }]);
      }
    } catch (error) {
      console.error('Failed to continue story:', error);
      toast.error('Failed to continue story. Please try again.');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [story]);

  // Handle custom input
  const handleCustomInput = useCallback(async (input: string) => {
    if (!story || story.metadata?.is_finished) return;

    setIsLoading(true);
    setStreamingText('');
    setIsStreaming(false);

    // Update last history entry with the custom input
    setHistory((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        custom_input: input,
      };
      return updated;
    });

    try {
      let finalChoices: any[] = [];
      let finalMetadata: any = null;
      let finalSceneText = '';
      let finalStorySummary = '';
      let accumulatedText = '';

      await continueStoryStream(
        {
          session_id: story.session_id,
          custom_input: input,
          story_summary: story.story_summary,
        },
        {
          onTextChunk: (chunk) => {
            accumulatedText += chunk;
            streamingBufferRef.current = accumulatedText;

            // Throttle UI updates to reduce re-renders
            const now = Date.now();
            if (now - lastUpdateTimeRef.current >= STREAMING_THROTTLE_MS) {
              const sceneText = extractSceneTextFromStream(accumulatedText);
              if (sceneText) {
                setIsStreaming(true);
                setStreamingText(sceneText);
                lastUpdateTimeRef.current = now;
              }
            }
          },
          onComplete: (choices, metadata, sceneText, storySummary) => {
            finalChoices = choices;
            finalMetadata = metadata;
            finalSceneText = sceneText || '';
            finalStorySummary = storySummary || '';
          },
          onError: (errorMsg) => {
            toast.error(errorMsg);
          },
        }
      );

      if (finalMetadata) {
        const response: StoryResponse = {
          session_id: story.session_id,
          current_scene: {
            scene_id: crypto.randomUUID(),
            text: finalSceneText || accumulatedText,
            timestamp: new Date().toISOString(),
          },
          choices: finalChoices.map((c) => ({
            choice_id: c.choice_id,
            text: c.text,
          })),
          story_summary: finalStorySummary || story.story_summary,
          metadata: finalMetadata,
        };

        setStory(response);
        // Add new scene to history
        setHistory((prev) => [...prev, { scene_text: finalSceneText || accumulatedText, turn_number: prev.length }]);
      }
    } catch (error) {
      console.error('Failed to continue story:', error);
      toast.error('Failed to continue story. Please try again.');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [story]);

  // Handle starting a new story
  const handleNewStory = useCallback(() => {
    setStory(null);
    setHistory([]);
    setSelectedTheme(null);
    setStreamingText('');
    setIsStreaming(false);
    setBookState('closed');
  }, []);

  // Get content for current state
  const getContent = () => {
    switch (bookState) {
      case 'theme-selection': {
        const { leftPage, rightPage } = ThemeSelectionContent({
          themes,
          selectedTheme,
          onSelectTheme: setSelectedTheme,
          onStartStory: handleStartStory,
          isLoading: themesLoading,
          playerName: playerName.trim(),
        });
        return <OpenBook leftContent={leftPage} rightContent={rightPage} />;
      }

      case 'playing':
        if (!story) {
          // Shouldn't happen, but fallback just in case
          return <LoadingScreen />;
        }
        return (
          <GameplayView
            story={story}
            streamingText={streamingText}
            isStreaming={isStreaming}
            isLoading={isLoading}
            history={history}
            onChoice={handleChoice}
            onCustomInput={handleCustomInput}
            onNewStory={handleNewStory}
          />
        );

      case 'loading':
        return <LoadingScreen />;

      default:
        return null;
    }
  };

  return (
    <div className="storybook-bg min-h-screen flex items-center justify-center p-4 md:p-8">
      <Toaster position="top-center" richColors />

      {/* Sparkles background */}
      <Sparkles count={30} />

      {/* Main content */}
      <div className="relative z-10 w-full">
        <AnimatePresence mode="wait">
          {/* Closed Book State */}
          {bookState === 'closed' && (
            <motion.div
              key="closed"
              exit={{ opacity: 0, scale: 0.9, rotateY: -30 }}
              transition={{ duration: 0.5 }}
            >
              <ClosedBook
                playerName={playerName}
                setPlayerName={setPlayerName}
                age={age}
                setAge={setAge}
                onOpen={handleOpenBook}
                isValid={isNameValid}
              />
            </motion.div>
          )}

          {/* Opening Animation */}
          {bookState === 'opening' && (
            <motion.div
              key="opening"
              className="flex items-center justify-center"
              initial={{ opacity: 1 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="book-cover w-full max-w-md aspect-[3/4]"
                animate={{
                  rotateY: [-10, -180],
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 1.5,
                  ease: [0.645, 0.045, 0.355, 1],
                }}
              >
                <CornerDecoration position="top-left" />
                <CornerDecoration position="top-right" />
                <CornerDecoration position="bottom-left" />
                <CornerDecoration position="bottom-right" />
                <div className="h-full flex items-center justify-center">
                  <h1 className="font-storybook-title text-4xl embossed">StoryQuest</h1>
                </div>
              </motion.div>
            </motion.div>
          )}

          {/* Open Book States */}
          {(bookState === 'theme-selection' || bookState === 'playing' || bookState === 'loading') && (
            <motion.div
              key="open"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              {getContent()}
            </motion.div>
          )}

          {/* Page Turning Animation */}
          {bookState === 'page-turning' && (
            <motion.div
              key="page-turn"
              className="flex items-center justify-center"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center">
                <motion.div
                  className="text-8xl"
                  animate={{ rotateY: [0, 360] }}
                  transition={{ duration: 0.8, ease: 'easeInOut' }}
                >
                  <span role="img" aria-label="book">
                    {'\uD83D\uDCDA'}
                  </span>
                </motion.div>
                <p className="font-storybook-heading text-xl text-storybook-gold-400 mt-4">
                  Turning to your adventure...
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default StorybookApp;
