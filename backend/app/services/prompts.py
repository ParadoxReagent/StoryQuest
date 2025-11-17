"""
LLM prompt templates for story generation.
Phase 1: Story format & API contract
Optimizations 9.2 & 9.3: Dynamic prompt adaptation and emotional arc guidance
"""

from typing import Dict


# Optimization 9.3: Emotional Arc Guidance
# Maps turn ranges to emotional tones for a structured narrative arc
EMOTIONAL_ARC = {
    1: "curious and inviting",
    2: "exciting and adventurous",
    3: "exciting and adventurous",
    4: "challenging with rising tension",
    5: "challenging with rising tension",
    6: "challenging with rising tension",
    7: "triumphant and satisfying",
    8: "triumphant and satisfying",
    "final": "peaceful and conclusive"
}


def get_emotional_tone(turn: int, max_turns: int) -> str:
    """
    Get the appropriate emotional tone for a given turn.

    Args:
        turn: Current turn number (1-indexed)
        max_turns: Total number of turns in the story

    Returns:
        Emotional tone description
    """
    if turn >= max_turns:
        return EMOTIONAL_ARC["final"]
    elif turn <= 1:
        return EMOTIONAL_ARC[1]
    elif turn <= 3:
        return EMOTIONAL_ARC.get(turn, EMOTIONAL_ARC[2])
    elif turn > max_turns - 3:
        # Climax phase (last 2-3 turns before final)
        return EMOTIONAL_ARC.get(7, EMOTIONAL_ARC[7])
    else:
        # Middle/challenging phase
        tone_key = min(turn, 6)
        return EMOTIONAL_ARC.get(tone_key, EMOTIONAL_ARC[4])


class StoryPrompts:
    """Template manager for LLM prompts."""

    @staticmethod
    def get_prompt_phase(turn: int, max_turns: int) -> str:
        """
        Optimization 9.2: Dynamic Prompt Adaptation
        Determine the story phase based on current turn and max turns.

        Args:
            turn: Current turn number (1-indexed, includes the turn about to be generated)
            max_turns: Maximum turns in the story

        Returns:
            Phase identifier: 'opening', 'adventure', 'wrapup', or 'ending'
        """
        if turn == 1:
            return 'opening'
        elif turn >= max_turns:
            return 'ending'
        elif turn >= max_turns - 2:  # Last 3 turns before final
            return 'wrapup'
        else:
            return 'adventure'

    @staticmethod
    def get_phase_guidance(phase: str) -> str:
        """
        Get prompt guidance based on story phase.

        Args:
            phase: Story phase ('opening', 'adventure', 'wrapup', 'ending')

        Returns:
            Guidance text for the LLM
        """
        guidance = {
            'opening': """
STORY PHASE: OPENING (Setting the Scene)
Focus on:
- Introducing the world and setting with vivid, welcoming descriptions
- Establishing a sense of wonder and excitement
- Making the player feel invited into this new world
- Creating a strong foundation for the adventure ahead
""",
            'adventure': """
STORY PHASE: ADVENTURE (Action & Discovery)
Focus on:
- Exciting discoveries and fun challenges
- Active exploration and problem-solving
- Meeting new friendly characters
- Building momentum with engaging activities
- Each scene should advance the story with new elements
""",
            'wrapup': """
STORY PHASE: WRAP-UP (Approaching Conclusion)
Focus on:
- Beginning to tie up loose ends
- Resolving any ongoing story threads
- Building toward a satisfying conclusion
- Avoid introducing new major characters or locations
- Choices should lead toward natural endings
""",
            'ending': """
STORY PHASE: ENDING (Final Scene)
This is the final turn - provide a complete, satisfying ending.
See the detailed ending instructions in the main prompt.
"""
        }
        return guidance.get(phase, guidance['adventure'])

    @staticmethod
    def get_story_continuation_prompt(
        age_range: str,
        story_summary: str,
        player_choice: str,
        player_name: str = "the player",
        turns_remaining: int | None = None,
        current_turn: int = 1,
        max_turns: int = 10,
        theme: str | None = None
    ) -> str:
        """
        Generate a prompt for continuing the story.
        Phase 6: Enhanced with stronger safety instructions.
        Optimizations 9.2 & 9.3: Dynamic prompt adaptation and emotional arc guidance.

        Args:
            age_range: Target age range (e.g., "6-8", "9-12")
            story_summary: Summary of the story so far
            player_choice: The action the player chose to take
            player_name: The player's name (default: "the player")
            turns_remaining: Number of turns remaining (deprecated, use current_turn/max_turns)
            current_turn: Current turn number (1-indexed)
            max_turns: Maximum turns in the story
            theme: Story theme (e.g., "space_adventure", "pirate_adventure")

        Returns:
            Formatted prompt string
        """
        # Optimization 9.2: Determine story phase
        phase = StoryPrompts.get_prompt_phase(current_turn, max_turns)
        phase_guidance = StoryPrompts.get_phase_guidance(phase)

        # Optimization 9.3: Get emotional tone for this turn
        emotional_tone = get_emotional_tone(current_turn, max_turns)

        wrap_guidance = ""
        is_final_turn = False
        if turns_remaining is not None:
            if turns_remaining <= 0:
                is_final_turn = True
                # For final turn, use completely different prompt structure
                return f"""⚠️⚠️⚠️ FINAL TURN - STORY ENDING ⚠️⚠️⚠️

You are writing THE FINAL SCENE of a children's story for ages {age_range}.
This is the LAST turn. The story ENDS after this scene. There are NO more turns.

STORY SUMMARY:
{story_summary}

PLAYER'S FINAL ACTION:
{player_name} chose: "{player_choice}"

🎯 YOUR PRIMARY MISSION 🎯
Write a COMPLETE, SATISFYING ENDING that wraps up the entire adventure.

MANDATORY ENDING STRUCTURE (Follow this exactly):
1. First 1-2 sentences: Show the result of the player's final action "{player_choice}"
2. Next 2-3 sentences: CONCLUDE the story with:
   - What {player_name} accomplished overall
   - How {player_name} feels (proud, happy, satisfied, content)
   - A sense of peaceful resolution and closure
   - Imply the ending through peaceful imagery and satisfied feelings:
     * Heading home, sunset, friends waving goodbye
     * Smiling, heart full of joy, feeling grateful
     * Looking back at the adventure, remembering the fun
   - AVOID always using direct phrases like "adventure ended", "journey was complete", "story was over"
   - SOMETIMES use subtle conclusive words like "finally" or "at last", but let the peaceful resolution speak for itself

❌ ABSOLUTELY FORBIDDEN - DO NOT DO THESE ❌
- NO questions (like "What will you do?" or "What do you think?")
- NO open-ended situations that need resolution
- NO hints about future adventures or "tomorrow" or "next time"
- NO "about to", "going to", "will", "soon", "later"
- NO new problems, mysteries, or discoveries
- NO asking the player/character anything
- NO conversations that continue beyond this scene

✅ GOOD ENDING EXAMPLES (Notice how these imply the ending without always saying "ended" or "complete"):

EXAMPLE 1 (Subtle - heading home):
"The robot happily showed you its favorite gear, a shiny golden one that sparkled beautifully. You smiled, feeling so proud of all the wonderful friends you had made today. As the stars began to twinkle outside, you waved goodbye and headed home, your heart full of happy memories."

EXAMPLE 2 (Subtle - peaceful moment):
"Sir Reginald smiled and pointed to a cloud shaped like a fluffy ice cream cone. 'That one is my favorite!' he said cheerfully. {player_name} laughed with joy as the sun began to set, painting the sky in beautiful colors. Together, they sat in comfortable silence, both grateful for the wonderful day they had shared."

EXAMPLE 3 (Slightly more direct, but still natural):
"You and your new friends gathered together and cheered with delight! Everyone had worked together so well. As you looked around at all the smiling faces, you knew this had been the best adventure ever. It was time to head home, and you couldn't wait to tell everyone about your amazing day!"

❌ BAD ENDING EXAMPLES (NEVER DO THIS):
"Sir Reginald asked, 'What shape do you see?' He waited for your answer." ← WRONG: Asking questions, waiting for response
"You were about to explore the next cave when..." ← WRONG: Suggesting continuation
"Tomorrow you would return to visit again!" ← WRONG: Future plans

SAFETY RULES:
- Only positive, happy, cheerful content
- Age-appropriate vocabulary for {age_range}
- No violence, scary content, or negativity
- G-rated and encouraging

Respond in this JSON format (NO choices field):
{{
  "scene_text": "The final scene that ENDS the story completely...",
  "story_summary_update": "Final summary of the completed adventure"
}}"""
            elif turns_remaining == 1:
                wrap_guidance = (
                    f"\n\n⚠️ PENULTIMATE TURN - ONE TURN LEFT ⚠️\n"
                    f"The next turn is the FINAL turn. After that, the story is OVER.\n\n"
                    f"REQUIREMENTS FOR THIS TURN:\n"
                    f"1. BEGIN wrapping up the adventure - this should feel like the climax\n"
                    f"2. RESOLVE any remaining plot threads or questions\n"
                    f"3. SHOW {player_name} succeeding or completing their main goal\n"
                    f"4. The 3 choices you provide should all lead directly to a satisfying conclusion\n"
                    f"5. Each choice should be a way to FINISH the story, not continue it\n\n"
                    f"FORBIDDEN:\n"
                    f"❌ NO new characters, locations, or major discoveries\n"
                    f"❌ NO new quests or challenges that can't be resolved in one turn\n"
                    f"❌ NO complex problems that need solving\n\n"
                    f"EXAMPLE CHOICES (steering toward ending):\n"
                    f"- \"Celebrate your success with your friends!\"\n"
                    f"- \"Take one last happy look around before heading home\"\n"
                    f"- \"Thank everyone who helped you on this adventure\""
                )
            elif turns_remaining <= 4:
                wrap_guidance = (
                    f"\n\nENDING SOON: Only {turns_remaining} turns remain. Begin wrapping up the adventure, tying loose ends, and guiding toward a happy ending. "
                    "Avoid introducing new characters or locations; focus on resolving what already exists and setting up the finale."
                )

        # Convert theme to readable format if provided
        theme_text = ""
        if theme:
            theme_readable = theme.replace("_", " ").title()
            theme_text = f"""
STORY THEME:
This is a {theme_readable} adventure. ALL scenes must relate to and stay within this theme.
Keep the story focused on {theme_readable} elements throughout.
"""

        return f"""You are a creative, kid-friendly storyteller for children aged {age_range}.
{theme_text}
STORY SO FAR:
{story_summary}

THE PLAYER JUST CHOSE THIS ACTION:
"{player_choice}"

{phase_guidance}

EMOTIONAL TONE FOR THIS SCENE:
The emotional tone for this turn should be: {emotional_tone}
Guide the narrative to reflect this emotional quality while maintaining a positive, age-appropriate atmosphere.

CRITICAL INSTRUCTION - STORY CONTINUITY:
You MUST continue the story directly based on the player's chosen action above. The next scene MUST show what happens as a direct result of "{player_choice}". Do NOT ignore this choice or take the story in a different direction. The player's choice is the foundation for what happens next.

CRITICAL SAFETY RULES (MUST FOLLOW):
1. ABSOLUTELY NO: violence, weapons, fighting, death, blood, injuries, pain, or hurt
2. ABSOLUTELY NO: scary content, monsters, ghosts, darkness, fear, or nightmares
3. ABSOLUTELY NO: mean words, bullying, name-calling, or negative language
4. ABSOLUTELY NO: sad, depressing, or hopeless situations
5. ONLY POSITIVE CONTENT: happy, fun, exciting, curious, friendly, helpful, kind
6. Age-appropriate vocabulary: simple, clear words appropriate for {age_range}
7. Everything must be G-rated and encouraging

CONTENT GUIDELINES:
- Start by showing the immediate result of the player's chosen action: "{player_choice}"
- Write 2-4 sentences describing what happens as a consequence of this specific choice
- The scene MUST directly relate to and follow from "{player_choice}"
{'' if is_final_turn else '- Generate exactly 3 fun, age-appropriate choices for what to do next'}
- Use cheerful, playful, encouraging language
- Include learning opportunities (curiosity, problem-solving, kindness)
- Make {player_name} feel heroic, capable, and valued
- Focus on friendship, discovery, creativity, and problem-solving
- Keep the tone light, positive, and uplifting
- No conflicts - only friendly cooperation and fun challenges
{wrap_guidance}

EXAMPLES OF GOOD CONTINUITY:
If player chose "Talk to the friendly robot":
- "You walk over to the cheerful robot and say hello! It beeps happily and shows you its amazing collection of colorful gears!"

If player chose "Explore the sparkly cave":
- "You step into the beautiful sparkly cave and gasp with delight! The walls shimmer with thousands of friendly glowing crystals that hum a gentle song!"

If player chose "Help the lost puppy":
- "You gently approach the small puppy and pet its soft fur. The puppy wags its tail excitedly and licks your hand, so happy you're here to help!"

EXAMPLES TO AVOID:
- Ignoring the player's choice and going in a completely different direction
- Anything involving danger, risk, or negative emotions
- Any form of conflict or opposition
- Dark, scary, or mysterious elements
- Complex or mature themes

Respond in this JSON format:
{{
  "scene_text": "What happens next as a direct result of the player's choice...",{'' if is_final_turn else '''
  "choices": [
    "Choice 1",
    "Choice 2",
    "Choice 3"
  ],'''}
  "story_summary_update": "Brief update to story summary including the player's action and what happened"
}}"""

    @staticmethod
    def get_story_start_prompt(
        player_name: str,
        age_range: str,
        theme: str
    ) -> str:
        """
        Generate a prompt for starting a new story.
        Optimization 9.3: Enhanced with emotional arc guidance for opening.

        Args:
            player_name: The player's name
            age_range: Target age range (e.g., "6-8", "9-12")
            theme: Story theme (e.g., "space_adventure", "magical_forest", or any dynamically generated theme)

        Returns:
            Formatted prompt string
        """
        # Convert theme ID to a human-readable description
        # Replace underscores with spaces and capitalize words
        theme_readable = theme.replace("_", " ").title()

        # Optimization 9.3: Opening scene should be "curious and inviting"
        opening_tone = EMOTIONAL_ARC[1]

        return f"""You are a creative, kid-friendly storyteller for children aged {age_range}.

Create the opening scene for a brand new story about {player_name}, who is about to begin an exciting {theme_readable} adventure.

EMOTIONAL TONE FOR THIS OPENING:
The emotional tone should be: {opening_tone}
Create a welcoming, intriguing atmosphere that invites the player into this new world.

CRITICAL SAFETY RULES (MUST FOLLOW):
1. ABSOLUTELY NO: violence, weapons, fighting, death, blood, injuries, pain, or hurt
2. ABSOLUTELY NO: scary content, monsters, ghosts, darkness, fear, or nightmares
3. ABSOLUTELY NO: mean words, bullying, name-calling, or negative language
4. ABSOLUTELY NO: sad, depressing, or hopeless situations
5. ONLY POSITIVE CONTENT: happy, fun, exciting, curious, friendly, helpful, kind
6. Age-appropriate vocabulary: simple, clear words appropriate for {age_range}
7. Everything must be G-rated, cheerful, and encouraging

CONTENT GUIDELINES:
- Write an exciting, cheerful opening (2-4 sentences) that introduces the setting and situation
- Generate exactly 3 fun, age-appropriate choices for what to do first
- Use playful, encouraging, positive language
- Make {player_name} the hero of the story - brave, clever, and kind
- Create a sense of wonder, excitement, and fun (not mystery or danger)
- Theme: {theme}
- Focus on discovery, friendship, and positive experiences
- Every element should feel safe, welcoming, and fun

EXAMPLES OF GOOD OPENINGS:
- "Welcome to the colorful Rainbow Space Station! You float past friendly alien flowers waving hello!"
- "You step into a magical forest where the trees sparkle with happy fireflies and cheerful birds sing!"
- "Dive into the warm, crystal-clear ocean where playful dolphins spin and dance in the sunshine!"

Respond in this JSON format:
{{
  "scene_text": "The opening scene description...",
  "choices": [
    "Choice 1",
    "Choice 2",
    "Choice 3"
  ],
  "story_summary_update": "{player_name} begins a {theme} adventure."
}}"""

    @staticmethod
    def get_system_message(age_range: str) -> str:
        """
        Get the system message for the LLM.

        Args:
            age_range: Target age range

        Returns:
            System message string
        """
        return f"""You are a professional children's storyteller specializing in interactive stories for ages {age_range}.

MANDATORY SAFETY REQUIREMENTS:
Your stories MUST NEVER contain:
- Violence, fighting, weapons, or any form of harm
- Scary content, monsters, ghosts, fear, or darkness
- Negative emotions like sadness, loneliness, or hopelessness
- Mean behavior, bullying, or unkind words
- Danger, risk, or threatening situations
- Complex or mature themes inappropriate for children

Your stories MUST ALWAYS be:
- Cheerful, positive, and uplifting
- Safe, friendly, and welcoming
- Age-appropriate with simple, clear vocabulary
- Focused on joy, discovery, friendship, and kindness
- Educational in subtle, fun ways (curiosity, problem-solving, cooperation)
- G-rated with only positive, encouraging content
- Full of wonder, excitement, and happy adventures

TONE: Enthusiastic, warm, encouraging, and celebratory
VOCABULARY: Simple, concrete, sensory words appropriate for {age_range}
STRUCTURE: Clear cause-and-effect, positive outcomes, growth through cooperation

Always respond with valid JSON in the exact format requested. Never deviate from safety guidelines."""
