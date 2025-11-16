# Adventure Game Optimization - Implementation Plan

## Project Overview

Transform a slow, single-model adventure game (5-10s per turn, expensive) into a fast, cost-effective experience using multi-tier models, streaming, pre-generation, and UX optimization.

**Current State:**
- Single Claude Sonnet model per turn
- 5-10 second wait times
- ~$0.05 per turn
- Poor user experience during loading

**Target State:**
- Two-tier model architecture (Architect + Narrator)
- <2 second perceived load time (streaming)
- ~$0.01 per turn (80% cost reduction)
- Instant responses for common choices (pre-generated)
- Professional loading states and UX

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME CONTROLLER                        │
│  - Manages game state                                       │
│  - Decides when to call Architect vs Narrator               │
│  - Handles caching and pre-generation                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
┌──────────────────────┐           ┌──────────────────────┐
│   ARCHITECT MODEL    │           │   NARRATOR MODEL     │
│   (Claude Sonnet)    │           │   (Claude Haiku)     │
│                      │           │                      │
│ • Plans story arcs   │           │ • Writes prose       │
│ • World state        │           │ • Expands sketches   │
│ • Beat sketches      │           │ • Generates choices  │
│ • Every 3-5 turns    │           │ • Every turn         │
│ • 2-5 seconds        │           │ • 1-2 seconds        │
│ • Returns sketches   │           │ • STREAMS output     │
└──────────────────────┘           └──────────────────────┘
            │                                   │
            │                                   │
            └─────────────────┬─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   CACHE LAYER    │
                    │ Pre-generated    │
                    │ Choice #1 results│
                    └──────────────────┘
```

---

## Phase 1: Foundation & Basic Streaming (Week 1)

**Goal:** Get streaming working with current single-model approach to immediately improve UX.

### 1.1 Set Up Project Structure

**Files to create:**
```
src/
├── services/
│   ├── claudeApi.js           # API wrapper with streaming support
│   └── storyGenerator.js      # Story generation logic
├── hooks/
│   ├── useStreamingResponse.js # React hook for streaming
│   └── useGameState.js         # Game state management
├── components/
│   ├── StoryDisplay.jsx        # Story text display with streaming
│   ├── ChoicePanel.jsx         # Choice buttons
│   ├── LoadingState.jsx        # Skeleton and loading animations
│   └── GameContainer.jsx       # Main game component
├── utils/
│   ├── promptBuilder.js        # Build prompts for models
│   └── jsonParser.js           # Parse streamed JSON
└── config/
    └── gameConfig.js           # Model names, API keys, settings
```

### 1.2 Implement Streaming API Client

**File: `src/services/claudeApi.js`**

```javascript
/**
 * Streaming Claude API client
 * 
 * Key features:
 * - Handles SSE (Server-Sent Events) streaming
 * - Parses chunks incrementally
 * - Error handling and retries
 * - Rate limiting
 */

export class ClaudeStreamingClient {
  constructor(apiKey = null) {
    this.apiUrl = 'https://api.anthropic.com/v1/messages';
    // API key handled by backend - no key needed in artifacts
  }

  async streamCompletion({ model, messages, maxTokens, onChunk, onComplete, onError }) {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          max_tokens: maxTokens,
          stream: true,
          messages
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      let fullText = '';
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'content_block_delta') {
                const text = data.delta?.text || '';
                fullText += text;
                onChunk(text, fullText);
              }
              
              if (data.type === 'message_stop') {
                onComplete(fullText);
              }
            } catch (e) {
              // Skip invalid JSON lines
            }
          }
        }
      }

      return fullText;
    } catch (error) {
      onError(error);
      throw error;
    }
  }
}
```

### 1.3 Create Streaming React Hook

**File: `src/hooks/useStreamingResponse.js`**

```javascript
import { useState, useCallback } from 'react';
import { ClaudeStreamingClient } from '../services/claudeApi';

export function useStreamingResponse() {
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const client = new ClaudeStreamingClient();

  const startStream = useCallback(async ({ model, messages, maxTokens }) => {
    setIsStreaming(true);
    setStreamingText('');
    setError(null);

    try {
      await client.streamCompletion({
        model,
        messages,
        maxTokens,
        onChunk: (chunk, fullText) => {
          setStreamingText(fullText);
        },
        onComplete: (fullText) => {
          setIsStreaming(false);
        },
        onError: (err) => {
          setError(err);
          setIsStreaming(false);
        }
      });
    } catch (err) {
      setError(err);
      setIsStreaming(false);
    }
  }, []);

  return {
    streamingText,
    isStreaming,
    error,
    startStream
  };
}
```

### 1.4 Build Loading State Component

**File: `src/components/LoadingState.jsx`**

```javascript
/**
 * Loading state with skeleton and contextual flavor text
 * 
 * Features:
 * - Animated skeleton lines
 * - Context-aware loading messages
 * - Smooth transitions
 */

export function LoadingState({ tone, context }) {
  const flavorMessages = {
    suspenseful: [
      "Tension builds as events unfold...",
      "The air grows heavy with anticipation...",
      "Something stirs in the darkness..."
    ],
    action: [
      "Chaos erupts around you...",
      "Time seems to slow as you react...",
      "Your reflexes take over..."
    ],
    mysterious: [
      "Strange forces stir in the shadows...",
      "Reality shifts at the edges of perception...",
      "The unknown beckons..."
    ],
    peaceful: [
      "A moment of calm settles over the scene...",
      "You take a breath and gather your thoughts...",
      "Serenity surrounds you..."
    ],
    default: [
      "The story continues...",
      "Your adventure unfolds...",
      "What happens next..."
    ]
  };

  const messages = flavorMessages[tone] || flavorMessages.default;
  const message = messages[Math.floor(Math.random() * messages.length)];

  return (
    <div className="loading-state">
      <div className="flavor-text">{message}</div>
      <div className="skeleton-container">
        <div className="skeleton-line long animate"></div>
        <div className="skeleton-line medium animate delay-1"></div>
        <div className="skeleton-line long animate delay-2"></div>
        <div className="skeleton-line short animate delay-3"></div>
      </div>
    </div>
  );
}
```

### 1.5 Create Story Display Component

**File: `src/components/StoryDisplay.jsx`**

```javascript
/**
 * Story display with streaming text support
 */

export function StoryDisplay({ text, isStreaming, tone }) {
  return (
    <div className="story-display">
      {isStreaming && text.length === 0 ? (
        <LoadingState tone={tone} />
      ) : (
        <div className="story-text">
          <p>{text}</p>
          {isStreaming && <span className="cursor-blink">▊</span>}
        </div>
      )}
    </div>
  );
}
```

### 1.6 Update Main Game Component

**File: `src/components/GameContainer.jsx`**

```javascript
import { useState } from 'react';
import { useStreamingResponse } from '../hooks/useStreamingResponse';
import { StoryDisplay } from './StoryDisplay';
import { ChoicePanel } from './ChoicePanel';

export function GameContainer() {
  const [gameHistory, setGameHistory] = useState([]);
  const [currentChoices, setCurrentChoices] = useState([]);
  const [choicesEnabled, setChoicesEnabled] = useState(true);
  
  const { streamingText, isStreaming, startStream } = useStreamingResponse();

  const handleChoice = async (choice) => {
    setChoicesEnabled(false);
    setCurrentChoices([]);

    await startStream({
      model: 'claude-sonnet-4-20250514', // Will change in Phase 2
      maxTokens: 800,
      messages: [{
        role: 'user',
        content: buildPrompt(choice, gameHistory)
      }]
    });

    // Parse response and extract choices
    try {
      const parsed = JSON.parse(streamingText);
      setCurrentChoices(parsed.choices);
      setGameHistory(prev => [...prev, { choice, response: parsed.narrative }]);
      
      // Dramatic pause before enabling choices
      setTimeout(() => setChoicesEnabled(true), 1500);
    } catch (err) {
      console.error('Failed to parse response:', err);
    }
  };

  return (
    <div className="game-container">
      <StoryDisplay 
        text={streamingText} 
        isStreaming={isStreaming}
        tone="suspenseful"
      />
      <ChoicePanel 
        choices={currentChoices}
        onChoiceSelect={handleChoice}
        enabled={choicesEnabled && !isStreaming}
      />
    </div>
  );
}
```

### 1.7 Testing Checklist

- [ ] Streaming displays text word-by-word (not all at once)
- [ ] Loading skeleton appears before text streams
- [ ] Choices are disabled during generation
- [ ] Dramatic pause (1.5s) enforced after text completes
- [ ] Error handling works (test with invalid API key)
- [ ] No duplicate API calls on rapid button clicks

**Success Metrics:**
- Text appears within 500ms (vs 5-10s wait)
- Users perceive 3-5x speed improvement
- No functionality broken from original version

---

## Phase 2: Two-Tier Model Architecture (Week 2)

**Goal:** Implement Architect (Sonnet) + Narrator (Haiku) separation to reduce costs and improve speed.

### 2.1 Create Model Service Layer

**File: `src/services/storyGenerator.js`**

```javascript
/**
 * Two-tier story generation system
 * 
 * ARCHITECT (Sonnet): Plans story arcs, world state, beat sketches
 * NARRATOR (Haiku): Writes prose from sketches, generates choices
 */

import { ClaudeStreamingClient } from './claudeApi';

export class StoryGenerator {
  constructor() {
    this.client = new ClaudeStreamingClient();
    this.worldState = {};
    this.plannedBeats = [];
    this.architectPromise = null;
  }

  /**
   * Architect: High-level story planning
   * Called every 3-5 turns or on major decisions
   */
  async updateArchitect(gameHistory, currentState) {
    const messages = [{
      role: 'user',
      content: `You are the story architect for this adventure game.

RECENT EVENTS:
${gameHistory.slice(-5).map(h => `- ${h.choice}: ${h.response}`).join('\n')}

CURRENT STATE:
${JSON.stringify(currentState, null, 2)}

Plan the next story arc. Respond with JSON:
{
  "world_state": {
    "player_status": "alive/wounded/etc",
    "location": "current location",
    "key_npcs": ["npc1", "npc2"],
    "active_quests": ["quest1"],
    "inventory_highlights": ["important item"],
    "relationships": {"npc_name": "friendly/hostile/neutral"},
    "world_changes": "what changed in the world"
  },
  "story_arc": {
    "current_phase": "rising_action/climax/etc",
    "tension_level": "low/medium/high",
    "next_major_event": "what big thing is coming"
  },
  "next_beats": [
    {
      "trigger": "when this beat activates",
      "summary": "2-3 sentence sketch of what happens",
      "tone": "suspenseful/action/peaceful/mysterious",
      "key_details": "specific details to include",
      "choices_preview": [
        {
          "text": "Choice 1 text",
          "leads_to": "Brief sketch of where this leads"
        },
        {
          "text": "Choice 2 text",
          "leads_to": "Brief sketch of where this leads"
        },
        {
          "text": "Choice 3 text",
          "leads_to": "Brief sketch of where this leads"
        }
      ]
    }
  ],
  "writing_instructions": {
    "tone": "overall tone to maintain",
    "focus": "what to emphasize (character/action/mystery)",
    "hint_at": "future event to foreshadow"
  }
}

Be concise but thorough. The beats will be expanded by another model.`
    }];

    try {
      let fullResponse = '';
      await this.client.streamCompletion({
        model: 'claude-sonnet-4-20250514',
        messages,
        maxTokens: 2000,
        onChunk: (chunk, full) => { fullResponse = full; },
        onComplete: () => {},
        onError: (err) => { throw err; }
      });

      const parsed = JSON.parse(fullResponse);
      this.worldState = parsed.world_state;
      this.plannedBeats = parsed.next_beats || [];
      this.writingInstructions = parsed.writing_instructions;
      this.storyArc = parsed.story_arc;

      return parsed;
    } catch (error) {
      console.error('Architect update failed:', error);
      throw error;
    }
  }

  /**
   * Narrator: Expand beat sketches into engaging prose
   * Called every turn with streaming
   */
  async generateNarrative({ choice, beat, worldState, onChunk, onComplete }) {
    const messages = [{
      role: 'user',
      content: `Expand this story beat into engaging prose (200-250 words).

USER ACTION: ${choice}

PLANNED BEAT: ${beat.summary}
KEY DETAILS TO INCLUDE: ${beat.key_details}
TONE: ${beat.tone}

WORLD STATE:
- Location: ${worldState.location}
- Status: ${worldState.player_status}
- Key NPCs nearby: ${worldState.key_npcs?.join(', ') || 'none'}

WRITING INSTRUCTIONS:
- Focus: ${this.writingInstructions?.focus}
- Hint at: ${this.writingInstructions?.hint_at}

Write naturally flowing narrative. Then provide exactly 3 choices.
Format as JSON:
{
  "narrative": "the prose here",
  "choices": ["choice 1", "choice 2", "choice 3"]
}

DO NOT use backticks or markdown. Output ONLY valid JSON.`
    }];

    try {
      let fullResponse = '';
      await this.client.streamCompletion({
        model: 'claude-haiku-4-20250514',
        messages,
        maxTokens: 700,
        onChunk: (chunk, full) => {
          fullResponse = full;
          onChunk(chunk, full);
        },
        onComplete: () => {
          try {
            // Strip any markdown if present
            const cleaned = fullResponse
              .replace(/```json\n?/g, '')
              .replace(/```\n?/g, '')
              .trim();
            const parsed = JSON.parse(cleaned);
            onComplete(parsed);
          } catch (err) {
            console.error('JSON parse error:', err);
            onComplete({
              narrative: fullResponse,
              choices: ["Continue", "Look around", "Rest"]
            });
          }
        },
        onError: (err) => { throw err; }
      });
    } catch (error) {
      console.error('Narrator generation failed:', error);
      throw error;
    }
  }

  /**
   * Determine if architect update is needed
   */
  shouldUpdateArchitect(turnCount, lastChoice) {
    const reasons = {
      scheduled: turnCount % 4 === 0,
      noBeats: this.plannedBeats.length === 0,
      majorDecision: this.isMajorDecision(lastChoice)
    };

    return Object.values(reasons).some(r => r);
  }

  /**
   * Detect major story decisions that need architect input
   */
  isMajorDecision(choice) {
    const majorKeywords = [
      'attack', 'kill', 'fight', 'battle',
      'romance', 'kiss', 'love',
      'betray', 'steal', 'lie',
      'confess', 'reveal',
      'leave', 'abandon', 'quit',
      'join', 'ally', 'agree',
      'refuse', 'deny', 'reject'
    ];

    const choiceLower = choice.toLowerCase();
    return majorKeywords.some(keyword => choiceLower.includes(keyword));
  }

  /**
   * Get default beat when none planned (fallback)
   */
  getDefaultBeat() {
    return {
      trigger: 'default',
      summary: 'Continue the adventure naturally based on recent events',
      tone: 'balanced',
      key_details: 'Maintain consistency with established world state',
      choices_preview: []
    };
  }
}
```

### 2.2 Update Game State Hook

**File: `src/hooks/useGameState.js`**

```javascript
import { useState, useCallback } from 'react';
import { StoryGenerator } from '../services/storyGenerator';

export function useGameState() {
  const [turnCount, setTurnCount] = useState(0);
  const [gameHistory, setGameHistory] = useState([]);
  const [worldState, setWorldState] = useState({});
  const [currentBeat, setCurrentBeat] = useState(null);
  
  const generator = useState(() => new StoryGenerator())[0];

  const initializeGame = useCallback(async () => {
    // Initialize with starting scenario
    const startingState = {
      location: 'village_square',
      player_status: 'healthy',
      key_npcs: [],
      inventory_highlights: [],
      relationships: {}
    };

    await generator.updateArchitect([], startingState);
    setWorldState(generator.worldState);
    setCurrentBeat(generator.plannedBeats[0]);
  }, [generator]);

  const processChoice = useCallback(async (choice, onStreamChunk, onComplete) => {
    const newTurnCount = turnCount + 1;
    setTurnCount(newTurnCount);

    // Check if we need architect update
    if (generator.shouldUpdateArchitect(newTurnCount, choice)) {
      console.log('🏗️ Updating architect...');
      await generator.updateArchitect(gameHistory, worldState);
      setWorldState(generator.worldState);
    }

    // Get current beat
    const beat = generator.plannedBeats.shift() || generator.getDefaultBeat();
    setCurrentBeat(beat);

    // Generate narrative
    await generator.generateNarrative({
      choice,
      beat,
      worldState: generator.worldState,
      onChunk: onStreamChunk,
      onComplete: (result) => {
        setGameHistory(prev => [...prev, {
          choice,
          response: result.narrative,
          beat: beat.trigger
        }]);
        onComplete(result);
      }
    });
  }, [turnCount, gameHistory, worldState, generator]);

  return {
    turnCount,
    gameHistory,
    worldState,
    currentBeat,
    initializeGame,
    processChoice
  };
}
```

### 2.3 Update Game Container

**File: `src/components/GameContainer.jsx`**

```javascript
import { useState, useEffect } from 'react';
import { useGameState } from '../hooks/useGameState';
import { StoryDisplay } from './StoryDisplay';
import { ChoicePanel } from './ChoicePanel';
import { LoadingState } from './LoadingState';

export function GameContainer() {
  const [streamingText, setStreamingText] = useState('');
  const [currentChoices, setCurrentChoices] = useState([]);
  const [choicesEnabled, setChoicesEnabled] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const {
    turnCount,
    currentBeat,
    initializeGame,
    processChoice
  } = useGameState();

  // Initialize game on mount
  useEffect(() => {
    initializeGame().then(() => {
      setStreamingText("Your adventure begins...");
      setCurrentChoices([
        "Explore the village",
        "Visit the tavern",
        "Head to the forest"
      ]);
      setChoicesEnabled(true);
    });
  }, []);

  const handleChoice = async (choice) => {
    setChoicesEnabled(false);
    setCurrentChoices([]);
    setStreamingText('');
    setIsGenerating(true);

    await processChoice(
      choice,
      (chunk, fullText) => {
        // Stream text to display
        setStreamingText(fullText);
      },
      (result) => {
        // Complete
        setCurrentChoices(result.choices);
        setIsGenerating(false);
        
        // Dramatic pause
        setTimeout(() => {
          setChoicesEnabled(true);
        }, 1500);
      }
    );
  };

  return (
    <div className="game-container">
      <div className="turn-counter">Turn {turnCount}</div>
      
      <StoryDisplay 
        text={streamingText}
        isStreaming={isGenerating}
        tone={currentBeat?.tone || 'default'}
      />
      
      <ChoicePanel 
        choices={currentChoices}
        onChoiceSelect={handleChoice}
        enabled={choicesEnabled && !isGenerating}
        customInputEnabled={choicesEnabled && !isGenerating}
      />
    </div>
  );
}
```

### 2.4 Testing Checklist

- [ ] Architect called on turns 0, 4, 8, 12... (every 4 turns)
- [ ] Architect called on major decisions (attack, betray, etc.)
- [ ] Narrator called every turn with streaming
- [ ] World state persists across turns
- [ ] Beat sketches successfully expand into prose
- [ ] Story maintains coherence across architect updates
- [ ] Cost per turn reduced (check API logs)

**Success Metrics:**
- Average turn cost: ~$0.01 (down from $0.05)
- Narrator response time: 1-2s (down from 5-10s)
- Story coherence maintained or improved

---

## Phase 3: Smart Pre-Generation & Caching (Week 3)

**Goal:** Pre-generate Choice #1 in background for near-instant responses on the most common path.

### 3.1 Create Cache Service

**File: `src/services/cacheService.js`**

```javascript
/**
 * Cache service for pre-generated story segments
 * 
 * Strategy: Pre-generate Choice #1 after each turn
 * - Uses architect's "leads_to" sketch
 * - Generates in background (non-blocking)
 * - Invalidates on world state changes
 */

export class StoryCache {
  constructor() {
    this.cache = new Map();
    this.maxSize = 10; // Keep last 10 pre-generations
  }

  /**
   * Generate cache key from choice and context
   */
  generateKey(choice, beatTrigger, turnCount) {
    return `${choice}|${beatTrigger}|${turnCount}`;
  }

  /**
   * Check if cached result exists and is valid
   */
  has(choice, beatTrigger, turnCount) {
    const key = this.generateKey(choice, beatTrigger, turnCount);
    return this.cache.has(key);
  }

  /**
   * Get cached result
   */
  get(choice, beatTrigger, turnCount) {
    const key = this.generateKey(choice, beatTrigger, turnCount);
    const cached = this.cache.get(key);
    
    if (cached) {
      console.log('⚡ Cache hit!', key);
      return cached;
    }
    
    return null;
  }

  /**
   * Store pre-generated result
   */
  set(choice, beatTrigger, turnCount, result) {
    const key = this.generateKey(choice, beatTrigger, turnCount);
    
    // LRU eviction
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    });
    
    console.log('💾 Cached result for:', key);
  }

  /**
   * Clear cache (on major state changes)
   */
  clear() {
    this.cache.clear();
    console.log('🗑️ Cache cleared');
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }
}
```

### 3.2 Add Pre-Generation to Story Generator

**File: `src/services/storyGenerator.js`** (add methods)

```javascript
// Add to StoryGenerator class:

  /**
   * Pre-generate narrative for a choice preview
   * Runs in background, non-blocking
   */
  async preGenerateChoice(choicePreview, worldState, cache, turnCount) {
    if (!choicePreview?.leads_to) return;

    try {
      console.log('🔮 Pre-generating:', choicePreview.text);

      const messages = [{
        role: 'user',
        content: `Expand this story sketch into engaging prose (200-250 words).

SKETCH: ${choicePreview.leads_to}

WORLD STATE:
${JSON.stringify(worldState, null, 2)}

Write naturally flowing narrative, then provide 3 new choices.
Format as JSON:
{
  "narrative": "prose here",
  "choices": ["choice 1", "choice 2", "choice 3"]
}

DO NOT use backticks. Output ONLY valid JSON.`
      }];

      let fullResponse = '';
      await this.client.streamCompletion({
        model: 'claude-haiku-4-20250514',
        messages,
        maxTokens: 700,
        onChunk: (chunk, full) => { fullResponse = full; },
        onComplete: () => {},
        onError: (err) => { throw err; }
      });

      // Parse and cache
      const cleaned = fullResponse
        .replace(/```json\n?/g, '')
        .replace(/```\n?/g, '')
        .trim();
      const parsed = JSON.parse(cleaned);

      // Cache the result
      cache.set(
        choicePreview.text,
        'pregenerated',
        turnCount + 1,
        parsed
      );

      console.log('✅ Pre-generation complete:', choicePreview.text);
    } catch (error) {
      console.warn('⚠️ Pre-generation failed:', error.message);
      // Silent failure - pre-gen is optional
    }
  }

  /**
   * Start background pre-generation for most likely choice
   */
  startBackgroundPreGen(currentBeat, worldState, cache, turnCount) {
    if (!currentBeat?.choices_preview?.[0]) return;

    const choice1Preview = currentBeat.choices_preview[0];
    
    // Fire and forget - don't await
    this.preGenerateChoice(choice1Preview, worldState, cache, turnCount)
      .catch(err => console.warn('Background pre-gen error:', err));
  }
```

### 3.3 Integrate Caching into Game State

**File: `src/hooks/useGameState.js`** (update)

```javascript
import { useState, useCallback, useRef } from 'react';
import { StoryGenerator } from '../services/storyGenerator';
import { StoryCache } from '../services/cacheService';

export function useGameState() {
  const [turnCount, setTurnCount] = useState(0);
  const [gameHistory, setGameHistory] = useState([]);
  const [worldState, setWorldState] = useState({});
  const [currentBeat, setCurrentBeat] = useState(null);
  const [cacheStats, setCacheStats] = useState({ hits: 0, misses: 0 });
  
  const generator = useState(() => new StoryGenerator())[0];
  const cache = useState(() => new StoryCache())[0];

  const processChoice = useCallback(async (choice, onStreamChunk, onComplete) => {
    const newTurnCount = turnCount + 1;
    setTurnCount(newTurnCount);

    // 🔍 CHECK CACHE FIRST
    const cached = cache.get(choice, currentBeat?.trigger, newTurnCount);
    if (cached) {
      console.log('⚡ Using cached response!');
      
      // Simulate streaming for UX consistency
      let index = 0;
      const text = cached.result.narrative;
      const interval = setInterval(() => {
        if (index < text.length) {
          onStreamChunk(text[index], text.slice(0, index + 1));
          index += 10; // Stream in chunks
        } else {
          clearInterval(interval);
          onComplete(cached.result);
          
          setCacheStats(prev => ({ ...prev, hits: prev.hits + 1 }));
        }
      }, 20);
      
      return;
    }

    setCacheStats(prev => ({ ...prev, misses: prev.misses + 1 }));

    // Check if we need architect update
    if (generator.shouldUpdateArchitect(newTurnCount, choice)) {
      console.log('🏗️ Updating architect...');
      cache.clear(); // Clear cache on major updates
      await generator.updateArchitect(gameHistory, worldState);
      setWorldState(generator.worldState);
    }

    // Get current beat
    const beat = generator.plannedBeats.shift() || generator.getDefaultBeat();
    setCurrentBeat(beat);

    // Generate narrative
    await generator.generateNarrative({
      choice,
      beat,
      worldState: generator.worldState,
      onChunk: onStreamChunk,
      onComplete: (result) => {
        setGameHistory(prev => [...prev, {
          choice,
          response: result.narrative,
          beat: beat.trigger
        }]);
        
        // 🔮 START BACKGROUND PRE-GENERATION
        generator.startBackgroundPreGen(
          beat,
          generator.worldState,
          cache,
          newTurnCount
        );
        
        onComplete(result);
      }
    });
  }, [turnCount, gameHistory, worldState, currentBeat, generator, cache]);

  return {
    turnCount,
    gameHistory,
    worldState,
    currentBeat,
    cacheStats,
    initializeGame,
    processChoice
  };
}
```

### 3.4 Add Cache Stats Display

**File: `src/components/DebugPanel.jsx`** (new component)

```javascript
/**
 * Debug panel showing cache performance (removable in production)
 */

export function DebugPanel({ cacheStats, turnCount, worldState }) {
  const hitRate = cacheStats.hits + cacheStats.misses > 0
    ? ((cacheStats.hits / (cacheStats.hits + cacheStats.misses)) * 100).toFixed(1)
    : 0;

  return (
    <div className="debug-panel">
      <h4>Debug Info</h4>
      <div className="debug-stat">
        <span>Turn:</span> <strong>{turnCount}</strong>
      </div>
      <div className="debug-stat">
        <span>Cache Hits:</span> <strong>{cacheStats.hits}</strong>
      </div>
      <div className="debug-stat">
        <span>Cache Misses:</span> <strong>{cacheStats.misses}</strong>
      </div>
      <div className="debug-stat">
        <span>Hit Rate:</span> <strong>{hitRate}%</strong>
      </div>
      <div className="debug-stat">
        <span>Location:</span> <strong>{worldState.location}</strong>
      </div>
    </div>
  );
}
```

### 3.5 Testing Checklist

- [ ] Choice #1 clicks show near-instant response (cached)
- [ ] Choice #2-3 still stream normally
- [ ] Cache invalidates on architect updates
- [ ] Pre-generation happens in background (doesn't block)
- [ ] Cache stats show hit rate improving over time
- [ ] No memory leaks from unbounded cache growth

**Success Metrics:**
- Choice #1 response time: <200ms (cached) vs 1-2s (uncached)
- Cache hit rate: 40-60% (most users pick Choice #1)
- No noticeable performance degradation

---

## Phase 4: Advanced UX Polish (Week 4)

**Goal:** Professional UI/UX with animations, better prompts, and edge case handling.

### 4.1 Enhanced Prompt Building

**File: `src/utils/promptBuilder.js`**

```javascript
/**
 * Centralized prompt building with templates
 * 
 * Benefits:
 * - Consistent formatting
 * - Easy A/B testing
 * - Version control for prompts
 */

export class PromptBuilder {
  
  /**
   * Architect prompt - story planning
   */
  static buildArchitectPrompt(gameHistory, currentState, turnCount) {
    const recentEvents = gameHistory
      .slice(-5)
      .map(h => `- ${h.choice} → ${h.response.slice(0, 100)}...`)
      .join('\n');

    return `You are the story architect for this adventure game.

GAME CONTEXT:
- Turn: ${turnCount}
- Recent events:
${recentEvents || '(Game just started)'}

CURRENT STATE:
${JSON.stringify(currentState, null, 2)}

Plan the next story arc with 3-4 beats. Each beat should be a sketch that can be expanded into 200-250 words.

Respond with JSON (no markdown, no backticks):
{
  "world_state": {
    "player_status": "healthy/wounded/exhausted/empowered",
    "location": "specific location name",
    "key_npcs": ["npc1 with brief description", "npc2..."],
    "active_quests": ["quest name and status"],
    "inventory_highlights": ["important items only"],
    "relationships": {"npc_name": "friendly/hostile/neutral/complex"},
    "world_changes": "what's different in the world now"
  },
  "story_arc": {
    "current_phase": "introduction/rising_action/climax/falling_action/resolution",
    "tension_level": "low/medium/high/extreme",
    "next_major_event": "what significant event is coming"
  },
  "next_beats": [
    {
      "trigger": "brief description of when this happens",
      "summary": "2-3 sentences describing this story moment",
      "tone": "suspenseful/action/peaceful/mysterious/dramatic/comedic",
      "key_details": "specific things that MUST appear in the prose",
      "choices_preview": [
        {"text": "Choice 1", "leads_to": "What happens if they pick this"},
        {"text": "Choice 2", "leads_to": "What happens if they pick this"},
        {"text": "Choice 3", "leads_to": "What happens if they pick this"}
      ]
    }
  ],
  "writing_instructions": {
    "tone": "dominant tone to maintain",
    "focus": "character_development/world_building/action/mystery/romance",
    "hint_at": "future plot point to foreshadow subtly"
  }
}`;
  }

  /**
   * Narrator prompt - prose generation
   */
  static buildNarratorPrompt(choice, beat, worldState, writingInstructions) {
    return `Expand this story beat into engaging prose.

USER ACTION: "${choice}"

BEAT TO EXPAND: ${beat.summary}

MUST INCLUDE: ${beat.key_details}

TONE: ${beat.tone}

CURRENT CONTEXT:
- Location: ${worldState.location}
- Player: ${worldState.player_status}
- NPCs present: ${worldState.key_npcs?.join(', ') || 'none'}
- Atmosphere: ${beat.tone}

WRITING GUIDELINES:
- Length: 200-250 words
- Style: ${writingInstructions?.focus || 'balanced'}
- Foreshadowing: ${writingInstructions?.hint_at || 'none'}
- Tone: ${writingInstructions?.tone || beat.tone}

Write immersive, present-tense prose. Show, don't tell. Use sensory details.

Then provide exactly 3 choices that feel natural and meaningful.

Format as JSON (no markdown, no backticks):
{
  "narrative": "The prose here. Use proper paragraphs if needed.",
  "choices": [
    "First choice - actionable and specific",
    "Second choice - clearly different from first",
    "Third choice - unique approach"
  ]
}`;
  }

  /**
   * Pre-generation prompt - expand sketch
   */
  static buildPreGenPrompt(choicePreview, worldState) {
    return `Expand this story sketch into prose.

SKETCH: ${choicePreview.leads_to}

WORLD CONTEXT:
${JSON.stringify(worldState, null, 2)}

Write 200-250 words of engaging narrative, then 3 new choices.

Format as JSON (no markdown):
{
  "narrative": "prose",
  "choices": ["choice 1", "choice 2", "choice 3"]
}`;
  }

  /**
   * Custom choice prompt - handle user's freeform input
   */
  static buildCustomChoicePrompt(customChoice, beat, worldState, gameHistory) {
    return `The player entered a custom action. Handle it gracefully.

PLAYER'S ACTION: "${customChoice}"

STORY CONTEXT: ${beat.summary}
CURRENT LOCATION: ${worldState.location}
PLAYER STATUS: ${worldState.player_status}

RECENT EVENTS:
${gameHistory.slice(-3).map(h => `- ${h.choice}`).join('\n')}

Determine if this action:
1. Makes sense in context → Execute it naturally
2. Is impossible/illogical → Gently redirect with consequences
3. Is creative/unexpected → Reward with interesting outcome

Write 200-250 words responding to their action, then 3 new choices.

Format as JSON (no markdown):
{
  "narrative": "prose response",
  "choices": ["choice 1", "choice 2", "choice 3"]
}`;
  }
}
```

### 4.2 Enhanced Choice Panel with Custom Input

**File: `src/components/ChoicePanel.jsx`**

```javascript
import { useState } from 'react';

export function ChoicePanel({ 
  choices, 
  onChoiceSelect, 
  enabled,
  customInputEnabled = true 
}) {
  const [customChoice, setCustomChoice] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (customChoice.trim()) {
      onChoiceSelect(customChoice.trim());
      setCustomChoice('');
      setShowCustomInput(false);
    }
  };

  return (
    <div className="choice-panel">
      <div className="predefined-choices">
        {choices.map((choice, index) => (
          <button
            key={index}
            className={`choice-btn ${!enabled ? 'disabled' : ''} ${index === 0 ? 'primary' : ''}`}
            onClick={() => onChoiceSelect(choice)}
            disabled={!enabled}
          >
            <span className="choice-text">{choice}</span>
            {index === 0 && enabled && (
              <span className="choice-hint">⚡ Instant</span>
            )}
          </button>
        ))}
      </div>

      {customInputEnabled && (
        <div className="custom-choice-section">
          {!showCustomInput ? (
            <button
              className="custom-choice-toggle"
              onClick={() => setShowCustomInput(true)}
              disabled={!enabled}
            >
              ✏️ Write your own action
            </button>
          ) : (
            <form onSubmit={handleCustomSubmit} className="custom-choice-form">
              <input
                type="text"
                value={customChoice}
                onChange={(e) => setCustomChoice(e.target.value)}
                placeholder="Describe what you want to do..."
                className="custom-choice-input"
                autoFocus
                maxLength={200}
                disabled={!enabled}
              />
              <div className="custom-choice-actions">
                <button 
                  type="submit" 
                  className="submit-btn"
                  disabled={!enabled || !customChoice.trim()}
                >
                  Submit
                </button>
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => {
                    setShowCustomInput(false);
                    setCustomChoice('');
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
```

### 4.3 CSS Animations & Styling

**File: `src/styles/game.css`**

```css
/* ============================================
   GAME CONTAINER
   ============================================ */

.game-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Georgia', serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  min-height: 100vh;
  color: #e0e0e0;
}

.turn-counter {
  text-align: right;
  font-size: 0.875rem;
  color: #888;
  margin-bottom: 1rem;
}

/* ============================================
   STORY DISPLAY
   ============================================ */

.story-display {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  min-height: 300px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.story-text {
  font-size: 1.125rem;
  line-height: 1.8;
  color: #f0f0f0;
}

.story-text p {
  margin-bottom: 1rem;
}

.cursor-blink {
  animation: blink 1s infinite;
  color: #4a9eff;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* ============================================
   LOADING STATE
   ============================================ */

.loading-state {
  padding: 2rem;
}

.flavor-text {
  font-style: italic;
  color: #aaa;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1rem;
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-line {
  height: 1rem;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  border-radius: 4px;
  background-size: 200% 100%;
}

.skeleton-line.long { width: 100%; }
.skeleton-line.medium { width: 80%; }
.skeleton-line.short { width: 60%; }

.skeleton-line.animate {
  animation: shimmer 2s infinite;
}

.skeleton-line.delay-1 {
  animation-delay: 0.2s;
}

.skeleton-line.delay-2 {
  animation-delay: 0.4s;
}

.skeleton-line.delay-3 {
  animation-delay: 0.6s;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ============================================
   CHOICE PANEL
   ============================================ */

.choice-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.predefined-choices {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.choice-btn {
  padding: 1rem 1.5rem;
  background: rgba(74, 158, 255, 0.1);
  border: 2px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
}

.choice-btn:hover:not(.disabled) {
  background: rgba(74, 158, 255, 0.2);
  border-color: rgba(74, 158, 255, 0.5);
  transform: translateX(4px);
}

.choice-btn.primary {
  border-color: rgba(74, 158, 255, 0.6);
  background: rgba(74, 158, 255, 0.15);
}

.choice-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.choice-hint {
  font-size: 0.75rem;
  background: rgba(255, 215, 0, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: #ffd700;
}

/* ============================================
   CUSTOM CHOICE INPUT
   ============================================ */

.custom-choice-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.custom-choice-toggle {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #aaa;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.custom-choice-toggle:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: #e0e0e0;
}

.custom-choice-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.custom-choice-input {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 1rem;
  width: 100%;
}

.custom-choice-input:focus {
  outline: none;
  border-color: rgba(74, 158, 255, 0.5);
}

.custom-choice-actions {
  display: flex;
  gap: 0.5rem;
}

.submit-btn, .cancel-btn {
  flex: 1;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn {
  background: rgba(74, 158, 255, 0.3);
  border: 2px solid rgba(74, 158, 255, 0.5);
  color: #e0e0e0;
}

.submit-btn:hover:not(:disabled) {
  background: rgba(74, 158, 255, 0.4);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: #aaa;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #e0e0e0;
}

/* ============================================
   DEBUG PANEL
   ============================================ */

.debug-panel {
  position: fixed;
  top: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 0.75rem;
  min-width: 200px;
}

.debug-panel h4 {
  margin: 0 0 0.5rem 0;
  color: #4a9eff;
}

.debug-stat {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  color: #aaa;
}

.debug-stat strong {
  color: #e0e0e0;
}

/* ============================================
   RESPONSIVE
   ============================================ */

@media (max-width: 768px) {
  .game-container {
    padding: 1rem;
  }

  .story-display {
    padding: 1.5rem;
  }

  .story-text {
    font-size: 1rem;
  }
}
```

### 4.4 Error Handling & Edge Cases

**File: `src/utils/errorHandler.js`**

```javascript
/**
 * Centralized error handling for graceful degradation
 */

export class GameErrorHandler {
  
  /**
   * Handle API errors with user-friendly messages
   */
  static handleApiError(error, context) {
    console.error(`API Error [${context}]:`, error);

    const errorMessages = {
      'rate_limit': 'Too many requests. Please wait a moment and try again.',
      'timeout': 'The request took too long. Please try again.',
      'network': 'Network error. Check your connection and try again.',
      'json_parse': 'Received invalid response. Trying again...',
      'default': 'Something went wrong. Please try again.'
    };

    const errorType = this.classifyError(error);
    return errorMessages[errorType] || errorMessages.default;
  }

  /**
   * Classify error type
   */
  static classifyError(error) {
    if (error.message?.includes('429')) return 'rate_limit';
    if (error.message?.includes('timeout')) return 'timeout';
    if (error.message?.includes('JSON')) return 'json_parse';
    if (error.message?.includes('fetch')) return 'network';
    return 'default';
  }

  /**
   * Provide fallback choices when generation fails
   */
  static getFallbackChoices(context = 'generic') {
    const fallbacks = {
      generic: [
        "Continue forward",
        "Look around carefully",
        "Take a moment to think"
      ],
      combat: [
        "Defend yourself",
        "Look for an escape",
        "Try to negotiate"
      ],
      dialogue: [
        "Listen carefully",
        "Ask a question",
        "End the conversation"
      ],
      exploration: [
        "Explore the area",
        "Return to safety",
        "Rest and recover"
      ]
    };

    return fallbacks[context] || fallbacks.generic;
  }

  /**
   * Retry with exponential backoff
   */
  static async retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        
        const delay = baseDelay * Math.pow(2, i);
        console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
}
```

### 4.5 Testing Checklist

- [ ] All animations smooth (no jank)
- [ ] Custom input validates properly
- [ ] Error messages appear for failed API calls
- [ ] Fallback choices work when generation fails
- [ ] UI remains responsive during slow API calls
- [ ] Debug panel shows accurate statistics
- [ ] Mobile layout works correctly
- [ ] Keyboard navigation functional

**Success Metrics:**
- Professional appearance
- Error recovery rate: 100%
- User can always make progress (fallback choices)
- No UI blocking or freezing

---

## Phase 5: Optimization & Production Readiness (Week 5)

**Goal:** Performance optimization, monitoring, and deployment preparation.

### 5.1 Performance Monitoring

**File: `src/services/performanceMonitor.js`**

```javascript
/**
 * Performance monitoring and analytics
 */

export class PerformanceMonitor {
  constructor() {
    this.metrics = {
      apiCalls: {
        architect: [],
        narrator: [],
        preGen: []
      },
      cachePerformance: {
        hits: 0,
        misses: 0
      },
      userExperience: {
        averageWaitTime: [],
        turnDurations: []
      },
      costs: {
        architectCalls: 0,
        narratorCalls: 0,
        preGenCalls: 0
      }
    };
  }

  /**
   * Log API call performance
   */
  logApiCall(type, duration, tokenCount) {
    this.metrics.apiCalls[type].push({
      timestamp: Date.now(),
      duration,
      tokenCount
    });

    // Increment cost counter
    this.metrics.costs[`${type}Calls`]++;
  }

  /**
   * Log cache hit/miss
   */
  logCache(hit) {
    if (hit) {
      this.metrics.cachePerformance.hits++;
    } else {
      this.metrics.cachePerformance.misses++;
    }
  }

  /**
   * Log user wait time
   */
  logWaitTime(duration) {
    this.metrics.userExperience.averageWaitTime.push(duration);
  }

  /**
   * Get summary report
   */
  getReport() {
    const architectCalls = this.metrics.apiCalls.architect.length;
    const narratorCalls = this.metrics.apiCalls.narrator.length;
    const totalCalls = architectCalls + narratorCalls;

    const avgArchitectTime = this.average(
      this.metrics.apiCalls.architect.map(c => c.duration)
    );
    const avgNarratorTime = this.average(
      this.metrics.apiCalls.narrator.map(c => c.duration)
    );

    const cacheHitRate = this.metrics.cachePerformance.hits /
      (this.metrics.cachePerformance.hits + this.metrics.cachePerformance.misses);

    // Estimated costs (approximate)
    const architectCost = architectCalls * 0.003; // ~$3 per 1000 calls
    const narratorCost = narratorCalls * 0.0004;  // ~$0.4 per 1000 calls
    const totalCost = architectCost + narratorCost;

    return {
      totalApiCalls: totalCalls,
      architectCalls,
      narratorCalls,
      avgArchitectTime: Math.round(avgArchitectTime),
      avgNarratorTime: Math.round(avgNarratorTime),
      cacheHitRate: (cacheHitRate * 100).toFixed(1) + '%',
      estimatedCost: `$${totalCost.toFixed(4)}`,
      avgUserWaitTime: Math.round(this.average(this.metrics.userExperience.averageWaitTime))
    };
  }

  average(arr) {
    if (arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }

  /**
   * Export metrics for analysis
   */
  exportMetrics() {
    return JSON.stringify(this.metrics, null, 2);
  }
}
```

### 5.2 Rate Limiting & Request Management

**File: `src/services/requestQueue.js`**

```javascript
/**
 * Request queue to prevent overwhelming API
 */

export class RequestQueue {
  constructor(maxConcurrent = 2) {
    this.maxConcurrent = maxConcurrent;
    this.running = 0;
    this.queue = [];
  }

  /**
   * Add request to queue
   */
  async enqueue(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.process();
    });
  }

  /**
   * Process queue
   */
  async process() {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }

    this.running++;
    const { fn, resolve, reject } = this.queue.shift();

    try {
      const result = await fn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.running--;
      this.process();
    }
  }

  /**
   * Get queue status
   */
  getStatus() {
    return {
      running: this.running,
      queued: this.queue.length
    };
  }
}
```

### 5.3 Save/Load System

**File: `src/services/saveSystem.js`**

```javascript
/**
 * Save and load game state
 */

export class SaveSystem {
  
  /**
   * Save game to localStorage
   */
  static saveGame(gameState, slotName = 'autosave') {
    try {
      const saveData = {
        version: '1.0',
        timestamp: Date.now(),
        gameState: {
          turnCount: gameState.turnCount,
          gameHistory: gameState.gameHistory,
          worldState: gameState.worldState,
          currentBeat: gameState.currentBeat
        }
      };

      localStorage.setItem(`adventure_save_${slotName}`, JSON.stringify(saveData));
      console.log('✅ Game saved:', slotName);
      return true;
    } catch (error) {
      console.error('❌ Save failed:', error);
      return false;
    }
  }

  /**
   * Load game from localStorage
   */
  static loadGame(slotName = 'autosave') {
    try {
      const data = localStorage.getItem(`adventure_save_${slotName}`);
      if (!data) return null;

      const saveData = JSON.parse(data);
      console.log('✅ Game loaded:', slotName);
      return saveData.gameState;
    } catch (error) {
      console.error('❌ Load failed:', error);
      return null;
    }
  }

  /**
   * Get all save slots
   */
  static getAllSaves() {
    const saves = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('adventure_save_')) {
        const data = JSON.parse(localStorage.getItem(key));
        saves.push({
          name: key.replace('adventure_save_', ''),
          timestamp: data.timestamp,
          turnCount: data.gameState.turnCount
        });
      }
    }
    return saves;
  }

  /**
   * Delete save
   */
  static deleteSave(slotName) {
    localStorage.removeItem(`adventure_save_${slotName}`);
  }

  /**
   * Auto-save every N turns
   */
  static enableAutoSave(gameStateGetter, interval = 5) {
    setInterval(() => {
      const state = gameStateGetter();
      if (state.turnCount > 0) {
        this.saveGame(state, 'autosave');
      }
    }, interval * 60 * 1000); // Convert to milliseconds
  }
}
```

### 5.4 Configuration Management

**File: `src/config/gameConfig.js`**

```javascript
/**
 * Centralized configuration
 */

export const GameConfig = {
  
  // Model configuration
  models: {
    architect: {
      name: 'claude-sonnet-4-20250514',
      maxTokens: 2000,
      updateFrequency: 4, // Every N turns
      temperature: 0.7
    },
    narrator: {
      name: 'claude-haiku-4-20250514',
      maxTokens: 700,
      temperature: 0.8
    }
  },

  // Cache configuration
  cache: {
    enabled: true,
    maxSize: 10,
    preGenEnabled: true,
    preGenChoice: 0 // Index of choice to pre-generate (0 = first)
  },

  // UX configuration
  ux: {
    dramaticPause: 1500, // ms before enabling choices
    streamingDelay: 20,  // ms between stream chunks
    skeletonEnabled: true,
    debugPanel: false // Set to false for production
  },

  // Performance
  performance: {
    maxConcurrentRequests: 2,
    requestTimeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000
  },

  // Game rules
  game: {
    maxHistoryLength: 50, // Trim history after this
    customChoiceEnabled: true,
    autoSaveInterval: 5, // minutes
    maxChoiceLength: 200 // characters
  },

  // Feature flags
  features: {
    twoTierModel: true,
    preGeneration: true,
    streaming: true,
    caching: true,
    saveSystem: true
  }
};

/**
 * Get estimated cost per turn
 */
export function getEstimatedCost() {
  const architectFreq = 1 / GameConfig.models.architect.updateFrequency;
  const narratorFreq = 1;
  
  // Approximate costs per call
  const architectCost = 0.003; // $3 per 1000 calls
  const narratorCost = 0.0004; // $0.4 per 1000 calls
  
  const avgCostPerTurn = 
    (architectFreq * architectCost) + 
    (narratorFreq * narratorCost);
  
  return avgCostPerTurn;
}
```

### 5.5 Testing Strategy Document

**File: `TESTING_GUIDE.md`**

```markdown
# Testing Guide

## Unit Tests

### Services
- [ ] `claudeApi.js` - streaming, error handling
- [ ] `storyGenerator.js` - architect/narrator separation
- [ ] `cacheService.js` - cache hit/miss, LRU eviction
- [ ] `promptBuilder.js` - prompt formatting

### Utilities
- [ ] `errorHandler.js` - error classification, retries
- [ ] `jsonParser.js` - streaming JSON parsing

## Integration Tests

### Story Flow
- [ ] Complete game loop (10 turns)
- [ ] Architect updates trigger correctly
- [ ] World state persists
- [ ] Choices lead to coherent narratives

### Caching
- [ ] Pre-generation completes in background
- [ ] Cache hits return instantly
- [ ] Cache invalidates on state changes

### Error Recovery
- [ ] API failures use fallback choices
- [ ] Retries work correctly
- [ ] User can always progress

## Performance Tests

### Metrics to Track
- [ ] Average API response time (narrator: <2s, architect: <5s)
- [ ] Cache hit rate (target: >40%)
- [ ] Cost per turn (target: <$0.015)
- [ ] Memory usage (no leaks over 100 turns)

### Load Testing
- [ ] Multiple concurrent games
- [ ] Rapid choice selection
- [ ] Long-running sessions (100+ turns)

## User Acceptance Tests

### UX Requirements
- [ ] Text appears within 500ms (streaming)
- [ ] Choices disabled during generation
- [ ] Loading states informative
- [ ] No UI freezing or jank

### Edge Cases
- [ ] Very long custom choices (200+ chars)
- [ ] Repeated identical choices
- [ ] Network disconnection/reconnection
- [ ] Page refresh (state recovery)

## Manual Testing Checklist

### Phase 1 - Streaming
- [ ] Start new game
- [ ] Verify text streams word-by-word
- [ ] Check skeleton appears first
- [ ] Confirm 1.5s pause before choices enable

### Phase 2 - Two-Tier Model
- [ ] Verify architect called on turn 0, 4, 8...
- [ ] Verify narrator called every turn
- [ ] Check world state updates
- [ ] Confirm cost reduction in logs

### Phase 3 - Caching
- [ ] Click choice #1 → should be instant (after first time)
- [ ] Click choice #2 → should stream normally
- [ ] Check cache stats in debug panel
- [ ] Verify pre-gen in browser console

### Phase 4 - UX Polish
- [ ] Test custom input
- [ ] Verify all animations smooth
- [ ] Check mobile responsiveness
- [ ] Test error scenarios (disable network)

### Phase 5 - Production
- [ ] Save/load game state
- [ ] Export performance report
- [ ] Verify autosave works
- [ ] Check all config options apply

## Regression Tests

Run after each phase to ensure previous features still work:
- [ ] Basic gameplay loop
- [ ] Streaming still functional
- [ ] Choices still generate properly
- [ ] Error handling works
```

### 5.6 Deployment Checklist

**File: `DEPLOYMENT_CHECKLIST.md`**

```markdown
# Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All console.logs removed or wrapped in debug flag
- [ ] No hardcoded API keys
- [ ] Error messages user-friendly
- [ ] Debug panel disabled (`GameConfig.ux.debugPanel = false`)

### Performance
- [ ] Production build created
- [ ] Bundle size optimized (<500KB)
- [ ] Images compressed
- [ ] Unused dependencies removed

### Testing
- [ ] All test suites pass
- [ ] Manual testing complete
- [ ] Edge cases handled
- [ ] Cross-browser tested (Chrome, Firefox, Safari)

### Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] User guide written
- [ ] Changelog updated

## Deployment

### Environment Setup
- [ ] Production API endpoint configured
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Error tracking setup (Sentry/similar)

### Database/Storage
- [ ] localStorage tested in target browsers
- [ ] Save/load system working
- [ ] Data migration plan (if needed)

### Security
- [ ] API keys secured (environment variables)
- [ ] CORS configured
- [ ] Input validation enabled
- [ ] XSS prevention checked

## Post-Deployment

### Monitoring
- [ ] Check error rates
- [ ] Monitor API usage
- [ ] Track performance metrics
- [ ] Watch cache hit rates

### User Feedback
- [ ] Feedback mechanism in place
- [ ] Support channel established
- [ ] Bug reporting process

### Optimization
- [ ] Review performance reports
- [ ] Adjust model parameters if needed
- [ ] Tune cache settings
- [ ] Optimize costs

## Rollback Plan

If issues occur:
1. [ ] Revert to previous version
2. [ ] Notify users of downtime
3. [ ] Investigate issues
4. [ ] Test fixes thoroughly
5. [ ] Redeploy with fixes
```

### 5.7 Final Testing Checklist

- [ ] All phases completed
- [ ] Performance report generated
- [ ] Cost per turn <$0.015
- [ ] Average narrator response <2s
- [ ] Cache hit rate >40%
- [ ] Zero blocking errors
- [ ] Save/load functional
- [ ] Mobile responsive
- [ ] All documentation complete

**Success Metrics:**
- 85% cost reduction (from $0.05 to <$0.015)
- 3-5x perceived speed improvement
- 40-60% cache hit rate
- Professional UI/UX
- Production-ready codebase

---

## Cost & Performance Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cost per turn | $0.050 | $0.012 | 76% reduction |
| Avg response time | 5-10s | 1-2s | 5x faster |
| Choice #1 response | 5-10s | <200ms | 25x+ faster |
| User experience | ⭐⭐ | ⭐⭐⭐⭐⭐ | Much better |

## Architecture Benefits

1. **Two-Tier Model**: Separates planning (expensive) from execution (cheap)
2. **Streaming**: Immediate feedback, no dead air
3. **Smart Caching**: Most common path is instant
4. **UX Polish**: Professional feel, handles all edge cases
5. **Monitoring**: Data-driven optimization

---

## Next Steps After Implementation

### Week 6+: Advanced Features

**Optional enhancements:**
- Voice narration (text-to-speech)
- Image generation for key moments
- Multiplayer support
- Achievement system
- Story branching visualization
- Export story as PDF/ebook
- Custom story templates
- Character creator
- Inventory system
- Combat mechanics

### Ongoing Maintenance

**Monthly tasks:**
- Review performance reports
- Optimize prompts based on user feedback
- Tune cache parameters
- Update models to latest versions
- Monitor costs and adjust if needed

### Analytics to Track

**Key metrics:**
- Daily active users
- Average session length
- Drop-off points
- Most/least used choices
- Custom choice frequency
- Error rates
- Cost per user session

---

## Troubleshooting Guide

### Common Issues

**Issue: Streaming not working**
- Check: Network tab for SSE connection
- Fix: Verify `stream: true` in API call

**Issue: JSON parse errors**
- Check: Response from API for markdown backticks
- Fix: Strip backticks before parsing

**Issue: Cache not hitting**
- Check: Key generation logic
- Fix: Ensure exact match on choice text

**Issue: High costs**
- Check: Architect call frequency
- Fix: Adjust `updateFrequency` in config

**Issue: Slow responses**
- Check: Token limits (maxTokens)
- Fix: Reduce if unnecessarily high

**Issue: State not persisting**
- Check: Browser localStorage capacity
- Fix: Trim old history entries

---

## File Structure Summary

```
src/
├── components/
│   ├── GameContainer.jsx          # Main game component
│   ├── StoryDisplay.jsx           # Story text display
│   ├── ChoicePanel.jsx            # Choice buttons + custom input
│   ├── LoadingState.jsx           # Skeleton + flavor text
│   └── DebugPanel.jsx             # Performance stats
├── hooks/
│   ├── useStreamingResponse.js    # Streaming API hook
│   └── useGameState.js            # Game state management
├── services/
│   ├── claudeApi.js               # API client with streaming
│   ├── storyGenerator.js          # Two-tier generation
│   ├── cacheService.js            # Pre-gen cache
│   ├── performanceMonitor.js      # Metrics tracking
│   ├── requestQueue.js            # Rate limiting
│   └── saveSystem.js              # Save/load
├── utils/
│   ├── promptBuilder.js           # Prompt templates
│   ├── errorHandler.js            # Error recovery
│   └── jsonParser.js              # Stream parsing
├── config/
│   └── gameConfig.js              # All settings
├── styles/
│   └── game.css                   # Complete styling
└── App.jsx                        # Root component
```

---

## Conclusion

This plan transforms your adventure game from:
- **Slow** (5-10s) → **Fast** (<2s, often instant)
- **Expensive** ($0.05/turn) → **Affordable** ($0.01/turn)
- **Basic** → **Professional** UX

Implementation is broken into 5 manageable phases, each building on the previous. The architecture is modular, testable, and production-ready.

**Recommended Timeline:**
- Week 1: Phase 1 (Streaming foundation)
- Week 2: Phase 2 (Two-tier models)
- Week 3: Phase 3 (Caching)
- Week 4: Phase 4 (UX polish)
- Week 5: Phase 5 (Production prep)

Good luck! 🚀
