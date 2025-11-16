/**
 * Main App Component
 * Phase 4: Minimal Web UI
 */

import { useState } from 'react';
import { startStoryStream, continueStoryStream } from './services/api';
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

const createScene = (text: string): StoryResponse['current_scene'] => ({
  scene_id:
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `scene-${Date.now()}-${Math.random().toString(16).slice(2)}`,
  text,
  timestamp: new Date().toISOString(),
});

const extractSceneTextFromStream = (buffer: string): string | null => {
  // Try to grab the scene_text value from streaming JSON chunks
  const match = buffer.match(/"scene_text"\s*:\s*"((?:\\.|[^"\\])*)/);
  if (!match) return null;

  try {
    return JSON.parse(`"${match[1]}"`);
  } catch {
    // Fallback: unescape basic sequences manually if JSON.parse fails mid-stream
    return match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
  }
};

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
  const [streamingText, setStreamingText] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState(false);

  /**
   * Start a new story
   */
  const handleStartStory = async (playerName: string, ageRange: string, theme: string) => {
    setIsLoading(true);
    setError(null);
    setAppState('loading');
    setStreamingText('');
    setIsStreaming(false);

    try {
      let sessionId = '';
      let finalChoices: any[] = [];
      let finalMetadata: any = null;
      let finalSceneText = '';
      let finalStorySummary = '';
      let accumulatedText = '';

      await startStoryStream(
        { player_name: playerName, age_range: ageRange, theme },
        {
          onSessionStart: (sid) => {
            sessionId = sid;
            setAppState('playing');
          },
          onTextChunk: (chunk) => {
            accumulatedText += chunk;
            const sceneText = extractSceneTextFromStream(accumulatedText);
            if (sceneText) {
              setIsStreaming(true);
              setStreamingText(sceneText);
            }
          },
          onComplete: (choices, metadata, sceneText, storySummary) => {
            finalChoices = choices;
            finalMetadata = metadata;
            finalSceneText = sceneText || '';
            finalStorySummary = storySummary || '';
          },
          onError: (errorMsg) => {
            setError(errorMsg);
            setAppState('error');
          },
        }
      );

      // After streaming completes, construct the story response
      if (finalMetadata && sessionId) {
        const response: StoryResponse = {
          session_id: sessionId,
          current_scene: createScene(finalSceneText || accumulatedText),
          choices: finalChoices.map((c) => ({
            choice_id: c.choice_id,
            text: c.text,
          })),
          story_summary: finalStorySummary || '',
          metadata: finalMetadata,
        };

        setStory(response);
        setHistory([
          {
            scene_text: accumulatedText,
            turn_number: 0,
          },
        ]);
      }
    } catch (err) {
      console.error('Failed to start story:', err);
      setError(getErrorMessage(err) || 'Failed to start story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  /**
   * Continue the story with a choice
   */
  const handleChoice = async (choice: { choice_id: string; text: string }) => {
    if (!story || story.metadata?.is_finished) return;

    setIsLoading(true);
    setError(null);
    setStreamingText('');
    // Don't set isStreaming until we actually receive text chunks
    setIsStreaming(false);

    // Add previous turn to history immediately
    const previousTurn: Turn = {
      scene_text: story.current_scene.text,
      player_choice: choice.text,
      turn_number: story.metadata?.turns || 0,
    };
    setHistory((prev) => [...prev, previousTurn]);

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
            const sceneText = extractSceneTextFromStream(accumulatedText);
            if (sceneText) {
              setIsStreaming(true);
              setStreamingText(sceneText);
            }
          },
          onComplete: (choices, metadata, sceneText, storySummary) => {
            finalChoices = choices;
            finalMetadata = metadata;
            finalSceneText = sceneText || '';
            finalStorySummary = storySummary || '';
          },
          onError: (errorMsg) => {
            setError(errorMsg);
            setAppState('error');
          },
        }
      );

      // After streaming completes, update the story
      if (finalMetadata) {
        const response: StoryResponse = {
          session_id: story.session_id,
          current_scene: createScene(finalSceneText || accumulatedText),
          choices: finalChoices.map((c) => ({
            choice_id: c.choice_id,
            text: c.text,
          })),
          story_summary: finalStorySummary || story.story_summary,
          metadata: finalMetadata,
        };

        setStory(response);
      }
    } catch (err) {
      console.error('Failed to continue story:', err);
      setError(getErrorMessage(err) || 'Failed to continue story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  /**
   * Continue the story with custom input
   */
  const handleCustomInput = async (input: string) => {
    if (!story || story.metadata?.is_finished) return;

    setIsLoading(true);
    setError(null);
    setStreamingText('');
    setIsStreaming(false);

    // Add previous turn to history immediately
    const previousTurn: Turn = {
      scene_text: story.current_scene.text,
      custom_input: input,
      turn_number: story.metadata?.turns || 0,
    };
    setHistory((prev) => [...prev, previousTurn]);

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
            const sceneText = extractSceneTextFromStream(accumulatedText);
            if (sceneText) {
              setIsStreaming(true);
              setStreamingText(sceneText);
            }
          },
          onComplete: (choices, metadata, sceneText, storySummary) => {
            finalChoices = choices;
            finalMetadata = metadata;
            finalSceneText = sceneText || '';
            finalStorySummary = storySummary || '';
          },
          onError: (errorMsg) => {
            setError(errorMsg);
            setAppState('error');
          },
        }
      );

      // After streaming completes, update the story
      if (finalMetadata) {
        const response: StoryResponse = {
          session_id: story.session_id,
          current_scene: createScene(finalSceneText || accumulatedText),
          choices: finalChoices.map((c) => ({
            choice_id: c.choice_id,
            text: c.text,
          })),
          story_summary: finalStorySummary || story.story_summary,
          metadata: finalMetadata,
        };

        setStory(response);
      }
    } catch (err) {
      console.error('Failed to continue story:', err);
      setError(getErrorMessage(err) || 'Failed to continue story. Please try again.');
      setAppState('error');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
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
      {/* Theme Selection and Loading/Error Screens - Traditional Layout */}
      {(appState === 'theme-selection' || appState === 'loading' || appState === 'error') && (
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
      )}

      {/* Playing Screen - New Optimized Layout */}
      {appState === 'playing' && story && (
        <div className="flex flex-col h-screen lg:grid lg:grid-cols-[2fr,1fr] lg:gap-0">
          {/* Left Column: Story Content (scrollable) */}
          <div className="flex-1 overflow-y-auto">
            <div className="container mx-auto px-4 md:px-6 py-4 md:py-6 space-y-4">
              {/* Header with New Story Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleNewStory}
                  disabled={isLoading}
                  className="px-4 py-2 md:px-6 md:py-3 rounded-xl border-4 border-white bg-white/20 hover:bg-white/30 text-white font-kid font-bold backdrop-blur-sm transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg text-sm md:text-base"
                  aria-label="Start new story"
                >
                  🔄 New Story
                </button>
              </div>

              {/* Story History - Mobile/Tablet */}
              {history.length > 1 && (
                <div className="lg:hidden">
                  <StoryHistory turns={history} />
                </div>
              )}

              {/* Current Story View */}
              <StoryView
                story={story}
                onChoiceClick={handleChoice}
                onCustomInput={handleCustomInput}
                disabled={isLoading}
                streamingText={streamingText}
                isStreaming={isStreaming}
              />
            </div>
          </div>

          {/* Right Column: Choices and History (Desktop only) */}
          <div className="hidden lg:flex lg:flex-col lg:border-l-4 lg:border-primary-200 lg:bg-gradient-to-b lg:from-primary-50 lg:to-white">
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Story History - Desktop */}
              {history.length > 1 && (
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 border-4 border-primary-200 shadow-lg">
                  <h3 className="font-kid text-xl font-bold text-primary-700 mb-3 flex items-center gap-2">
                    <span className="text-2xl">📖</span>
                    Story So Far
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {history.map((turn) => (
                      <div
                        key={turn.turn_number}
                        className="border-l-4 border-primary-400 pl-3 py-2 bg-white/50 rounded-r-lg"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-kid text-xs font-bold text-primary-600">
                            Turn {turn.turn_number}
                          </span>
                          {turn.turn_number === 0 && (
                            <span className="text-xs font-kid bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                              Start
                            </span>
                          )}
                        </div>
                        <p className="font-kid text-sm text-gray-700 line-clamp-3">
                          {turn.scene_text}
                        </p>
                        {(turn.player_choice || turn.custom_input) && (
                          <p className="font-kid text-xs text-primary-600 italic mt-1">
                            → {turn.custom_input || turn.player_choice}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
