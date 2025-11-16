/**
 * Custom hook to throttle text streaming display
 * Provides smooth, consistent text appearance regardless of token arrival speed
 *
 * This prevents flickering when LLMs generate tokens very quickly by controlling
 * the visual display rate independently of token arrival rate.
 *
 * PERFORMANCE TUNING:
 * - For slower, more deliberate typing effect: Decrease charsPerFrame (e.g., 1-2)
 *   or increase frameDelay (e.g., 40-50ms)
 * - For faster reveals: Increase charsPerFrame (e.g., 4-6) or decrease frameDelay (e.g., 15-20ms)
 * - Current defaults provide a smooth ~150 characters/second reveal rate
 */

import { useState, useEffect, useRef } from 'react';

interface UseThrottledTextOptions {
  /** Characters to reveal per animation frame (default: 2) */
  charsPerFrame?: number;
  /** Milliseconds between frames (default: 30ms) */
  frameDelay?: number;
}

/**
 * Hook that throttles text display for smooth streaming animation
 * @param sourceText - The actual streaming text from the API
 * @param isStreaming - Whether streaming is currently active
 * @param options - Configuration options
 * @returns The throttled text to display
 */
export function useThrottledText(
  sourceText: string,
  isStreaming: boolean,
  options: UseThrottledTextOptions = {}
): string {
  const { charsPerFrame = 2, frameDelay = 30 } = options;

  const [displayedText, setDisplayedText] = useState('');
  const displayedLengthRef = useRef(0);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    // If not streaming, show full text immediately
    if (!isStreaming) {
      setDisplayedText(sourceText);
      displayedLengthRef.current = sourceText.length;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // If streaming, gradually reveal text
    if (displayedLengthRef.current < sourceText.length) {
      // Clear any existing interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      // Create new interval to gradually reveal text
      intervalRef.current = setInterval(() => {
        setDisplayedText(() => {
          const currentLength = displayedLengthRef.current;
          const targetLength = sourceText.length;

          // If we've caught up, stop
          if (currentLength >= targetLength) {
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }
            return sourceText;
          }

          // Reveal more characters
          const newLength = Math.min(currentLength + charsPerFrame, targetLength);
          displayedLengthRef.current = newLength;
          return sourceText.substring(0, newLength);
        });
      }, frameDelay);
    }

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [sourceText, isStreaming, charsPerFrame, frameDelay]);

  // Reset when source text becomes empty (new story/turn)
  useEffect(() => {
    if (sourceText === '') {
      setDisplayedText('');
      displayedLengthRef.current = 0;
    }
  }, [sourceText]);

  return displayedText;
}
