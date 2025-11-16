/**
 * Main App Component
 * Phase 4: Minimal Web UI
 */

import { useState } from 'react';
import { startStory, continueStory } from './services/api';
import type { StoryResponse } from './types/api';
import ThemeSelection from './components/ThemeSelection';
import StoryView from './components/StoryView';
import StoryHistory from './components/StoryHistory';

type AppState = 'theme-selection' | 'playing' | 'loading' | 'error';

interface Turn {
  scene_text: string;
  player_choice?: string;
  custom_input?: string;
  turn_number: number;
}

const getErrorMessage = (error: unknown): string => {
  if (typeof error === 'object' && error !== null) {
    const maybeResponse = (error as { response?: { data?: { detail?: string } } }).response;
    if (maybeResponse?.data?.detail) {
      return maybeResponse.data.detail;
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Something went wrong. Please try again.';
};

function App() {
  const [appState, setAppState] = useState<AppState>('theme-selection');
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [history, setHistory] = useState<Turn[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Start a new story
   */
  const handleStartStory = async (playerName: string, ageRange: string, theme: string) => {
    setIsLoading(true);
    setError(null);
    setAppState('loading');

    try {
      const response = await startStory({ player_name: playerName, age_range: ageRange, theme });
      setStory(response);
      setHistory([
        {
          scene_text: response.current_scene.text,
          turn_number: 0,
        },
      ]);
      setAppState('playing');
    } catch (err) {
      console.error('Failed to start story:', err);
      setError(getErrorMessage(err) || 'Failed to start story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Continue the story with a choice
   */
  const handleChoice = async (choiceId: string) => {
    if (!story) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await continueStory({
        session_id: story.session_id,
        choice_id: choiceId,
        story_summary: story.story_summary,
      });

      // Add previous turn to history
      const previousTurn: Turn = {
        scene_text: story.current_scene.text,
        player_choice: choiceId,
        turn_number: story.metadata?.turns || 0,
      };

      setHistory((prev) => [...prev, previousTurn]);
      setStory(response);
    } catch (err) {
      console.error('Failed to continue story:', err);
      setError(getErrorMessage(err) || 'Failed to continue story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Continue the story with custom input
   */
  const handleCustomInput = async (input: string) => {
    if (!story) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await continueStory({
        session_id: story.session_id,
        custom_input: input,
        story_summary: story.story_summary,
      });

      // Add previous turn to history
      const previousTurn: Turn = {
        scene_text: story.current_scene.text,
        custom_input: input,
        turn_number: story.metadata?.turns || 0,
      };

      setHistory((prev) => [...prev, previousTurn]);
      setStory(response);
    } catch (err) {
      console.error('Failed to continue story:', err);
      setError(getErrorMessage(err) || 'Failed to continue story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Reset and start a new story
   */
  const handleNewStory = () => {
    setStory(null);
    setHistory([]);
    setError(null);
    setAppState('theme-selection');
  };

  /**
   * Retry after error
   */
  const handleRetry = () => {
    setError(null);
    if (story) {
      setAppState('playing');
    } else {
      setAppState('theme-selection');
    }
  };

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        {/* Theme Selection Screen */}
        {appState === 'theme-selection' && (
          <ThemeSelection onStart={handleStartStory} disabled={isLoading} />
        )}

        {/* Loading Screen */}
        {appState === 'loading' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white p-12 rounded-2xl border-4 border-primary-400 shadow-2xl text-center">
              <div className="animate-bounce text-8xl mb-6">✨</div>
              <h2 className="font-kid text-3xl font-bold text-primary-600 mb-4">
                Creating your amazing story...
              </h2>
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-16 w-16 border-8 border-primary-500 border-t-transparent"></div>
              </div>
            </div>
          </div>
        )}

        {/* Playing Screen */}
        {appState === 'playing' && story && (
          <div className="space-y-6">
            {/* Header with New Story Button */}
            <div className="max-w-4xl mx-auto flex justify-end">
              <button
                onClick={handleNewStory}
                disabled={isLoading}
                className="px-6 py-3 rounded-xl border-4 border-white bg-white/20 hover:bg-white/30 text-white font-kid font-bold backdrop-blur-sm transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                aria-label="Start new story"
              >
                🔄 New Story
              </button>
            </div>

            {/* Story History */}
            {history.length > 1 && (
              <StoryHistory turns={history} />
            )}

            {/* Current Story View */}
            <StoryView
              story={story}
              onChoiceClick={handleChoice}
              onCustomInput={handleCustomInput}
              disabled={isLoading}
            />
          </div>
        )}

        {/* Error Screen */}
        {appState === 'error' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white p-12 rounded-2xl border-4 border-red-400 shadow-2xl">
              <div className="text-center mb-6">
                <div className="text-8xl mb-4">😕</div>
                <h2 className="font-kid text-3xl font-bold text-red-600 mb-4">
                  Oops! Something went wrong
                </h2>
                {error && (
                  <p className="font-kid text-lg text-gray-700 mb-6">
                    {error}
                  </p>
                )}
              </div>

              <div className="flex gap-4 justify-center">
                <button
                  onClick={handleRetry}
                  className="px-8 py-4 rounded-xl border-4 border-primary-400 bg-primary-500 text-white font-kid text-xl font-bold hover:bg-primary-600 transition-all duration-200 hover:scale-105 shadow-lg"
                  aria-label="Try again"
                >
                  🔄 Try Again
                </button>
                <button
                  onClick={handleNewStory}
                  className="px-8 py-4 rounded-xl border-4 border-gray-300 bg-white text-gray-700 font-kid text-xl font-bold hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg"
                  aria-label="Start over"
                >
                  🏠 Start Over
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
