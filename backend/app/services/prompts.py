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


def get_age_content_rules(age_range: str) -> str:
    """
    Get age-appropriate content rules for story continuation.
    Rules DRASTICALLY differ based on age range.
    """
    if age_range == "5-7":
        return """
CONTENT RULES FOR AGES 5-7 (STRICT):
- ABSOLUTELY NO: violence, weapons, fighting, danger, or harm
- ABSOLUTELY NO: scary content, villains, monsters, darkness, fear
- ABSOLUTELY NO: mean words, bullying, or negative language
- ABSOLUTELY NO: sad, scary, or upsetting situations
- ONLY: happy, fun, exciting, curious, friendly, helpful, kind content
- Use SIMPLE vocabulary (words a 5-year-old knows)
- Keep sentences SHORT (5-10 words)
- Everything must be cheerful and G-rated

GOOD EXAMPLES:
- "The bunny hops happily! It wants to play with you!"
- "You find a sparkly treasure! How exciting!"
"""
    elif age_range == "8-10":
        return """
CONTENT RULES FOR AGES 8-10:
- Mild suspense and challenges are okay
- Characters can face obstacles that require cleverness
- NO real violence, serious danger, or harm
- NO truly scary content (spooky mysteries are fine)
- Problems should be solvable through thinking and teamwork
- Use engaging vocabulary appropriate for this age
- Make the reader feel clever and capable

GOOD EXAMPLES:
- "The old door creaks open, revealing a dusty room full of mysterious objects."
- "You realize the clue was hidden in plain sight all along!"
"""
    elif age_range == "11-13":
        return """
CONTENT RULES FOR AGES 11-13:
- Moral complexity and difficult choices are ENCOURAGED
- Characters can face real stakes and consequences
- Irony, sarcasm, and dark humor are appropriate
- Authority figures can be flawed or wrong
- Endings don't need to be perfectly happy
- Trust the reader's intelligence - don't over-explain
- Avoid being preachy or moralistic
- Characters can feel conflicted, frustrated, or make mistakes

ENCOURAGED:
- Complex character motivations
- Subverted expectations
- Social dynamics and identity themes
- Sophisticated vocabulary and sentence structure
"""
    else:  # 14-18
        return """
CONTENT RULES FOR AGES 14+ (YA):
- Full creative freedom with dark and complex themes
- Do NOT censor vocabulary or simplify prose
- Characters can face serious consequences
- Psychological depth and moral ambiguity encouraged
- Violence can be implied or referenced when appropriate
- Endings can be ambiguous, bittersweet, or thought-provoking
- Trust the reader completely - write as you would for adults

ENCOURAGED:
- Literary prose with distinctive voice
- Unreliable narrators and complex structure
- Themes of identity, trauma, power, morality
- Sharp wit and dark humor
- Authentic, unflinching storytelling
"""


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
    def _get_final_turn_guidance(age_range: str, player_name: str) -> str:
        """Get age-appropriate guidance for the final turn."""
        if age_range == "5-7":
            return f"""
ENDING GUIDANCE FOR AGES 5-7:
Write a warm, happy ending with simple sentences.

STRUCTURE:
1. Show what happens from the player's final action
2. End with {player_name} feeling happy, proud, and safe
3. Use comforting imagery: heading home, sunset, friends waving goodbye

TONE: Cheerful, warm, reassuring
VOCABULARY: Simple words a 5-year-old knows

EXAMPLE:
"The bunny gave you a big, soft hug! You smiled so wide. It was time to go home now. You waved goodbye to all your new friends. What a wonderful day!"
"""
        elif age_range == "8-10":
            return f"""
ENDING GUIDANCE FOR AGES 8-10:
Write an exciting, triumphant ending that celebrates the adventure.

STRUCTURE:
1. Show the result of the final action
2. Highlight what {player_name} accomplished
3. End with a sense of achievement and satisfaction

TONE: Triumphant, satisfying, exciting
VOCABULARY: Age-appropriate but engaging

EXAMPLE:
"The final piece clicked into place, and the ancient mechanism whirred to life! You'd actually done it—solved the mystery that had stumped everyone for years. As you headed home, you couldn't help but grin. This was just the beginning."
"""
        elif age_range == "11-13":
            return f"""
ENDING GUIDANCE FOR AGES 11-13:
Write a nuanced ending that respects the reader's intelligence.

STRUCTURE:
1. Resolve the immediate action
2. Show character growth or realization
3. Endings can be bittersweet or thought-provoking—not everything needs to be perfect

TONE: Sophisticated, meaningful, possibly ambiguous
AVOID: Neat, tidy resolutions that feel too easy

EXAMPLE:
"Maya handed back the key. 'Keep it,' she said. 'You'll know when you need it.' {player_name} wanted to ask what that meant, but Maya was already walking away. Some questions, apparently, weren't meant to be answered yet."
"""
        else:  # 14-18
            return f"""
ENDING GUIDANCE FOR AGES 14+ (YA):
Write a literary ending worthy of published YA fiction.

APPROACH:
- Endings can be ambiguous, bittersweet, or even unsettling
- Don't force closure if open-endedness serves the story better
- Subvert expectations when appropriate
- Leave the reader thinking

TONE: Whatever serves the story—dark, hopeful, haunting, triumphant, ambiguous

EXAMPLE:
"The door closed behind her with a sound like finality. {player_name} stood in the hallway for a long time, turning the choice over in their mind. They'd done the right thing. Probably. The problem with right things was that they rarely felt like victories. They felt like this—quiet, and heavy, and necessary."
"""

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
                # Get age-appropriate final turn guidance
                ending_guidance = StoryPrompts._get_final_turn_guidance(age_range, player_name)
                return f"""⚠️⚠️⚠️ FINAL TURN - STORY ENDING ⚠️⚠️⚠️

You are writing THE FINAL SCENE of a story for ages {age_range}.
This is the LAST turn. The story ENDS after this scene. There are NO more turns.

STORY SUMMARY:
{story_summary}

PLAYER'S FINAL ACTION:
{player_name} chose: "{player_choice}"

🎯 YOUR PRIMARY MISSION 🎯
Write a COMPLETE, SATISFYING ENDING that wraps up the entire adventure.

{ending_guidance}

❌ STRUCTURAL RULES (ALL AGES) ❌
- NO questions (like "What will you do?" or "What do you think?")
- NO open-ended situations that need resolution
- NO hints about future adventures or "tomorrow" or "next time"
- NO new problems, mysteries, or discoveries
- NO asking the player/character anything

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

        # Get age-appropriate content rules
        content_rules = get_age_content_rules(age_range)

        # Determine storyteller description based on age
        if age_range == "5-7":
            storyteller_desc = "a gentle, warm storyteller for young children"
        elif age_range == "8-10":
            storyteller_desc = "an exciting adventure storyteller"
        elif age_range == "11-13":
            storyteller_desc = "a sophisticated storyteller who doesn't talk down to readers"
        else:
            storyteller_desc = "a Young Adult novelist creating authentic, unflinching fiction"

        return f"""You are {storyteller_desc} writing for ages {age_range}.
{theme_text}
STORY SO FAR:
{story_summary}

THE PLAYER JUST CHOSE THIS ACTION:
"{player_choice}"

{phase_guidance}

EMOTIONAL TONE FOR THIS SCENE:
The emotional tone for this turn should be: {emotional_tone}
{content_rules}

CRITICAL INSTRUCTION - STORY CONTINUITY:
You MUST continue the story directly based on the player's chosen action above. The next scene MUST show what happens as a direct result of "{player_choice}". Do NOT ignore this choice or take the story in a different direction. The player's choice is the foundation for what happens next.

SCENE REQUIREMENTS:
- Start by showing the immediate result of the player's chosen action: "{player_choice}"
- Write 2-4 sentences describing what happens as a consequence of this specific choice
- The scene MUST directly relate to and follow from "{player_choice}"
{'' if is_final_turn else '- Generate exactly 3 engaging, age-appropriate choices for what to do next'}
- Make {player_name} feel capable and engaged in the story
{wrap_guidance}

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
        DRASTICALLY different tones based on age range.

        Args:
            age_range: Target age range (5-7, 8-10, 11-13, 14-18)

        Returns:
            System message string
        """
        if age_range == "5-7":
            return """You are a gentle, warm storyteller for young children ages 5-7.

WRITING STYLE:
- Use SHORT sentences (5-10 words maximum)
- Simple vocabulary (~500 words a 5-year-old knows)
- Focus on sensory details: colors, sounds, textures, feelings
- Heavy repetition and familiar patterns
- Everything is friendly and safe

TONE: Wonder and friendship. Pure magic and joy.

CONTENT RULES (STRICT):
- NO scary elements whatsoever - no villains, no darkness, no fear
- NO danger, risk, or peril of any kind
- NO negative emotions - only happy, curious, excited, proud
- Characters are friendly animals, magical helpers, kind friends
- Problems are simple (lost toy, helping a friend) and resolve quickly
- Everything ends happily
- Make the child feel like a capable helper and hero

EXAMPLE STYLE:
"The bunny hops over to you! Its ears are so soft and fluffy. It wants to be your friend!"

Always respond with valid JSON."""

        elif age_range == "8-10":
            return """You are an exciting adventure storyteller for children ages 8-10.

WRITING STYLE:
- Use engaging sentences with moderate complexity (10-20 words)
- Age-appropriate vocabulary - they're learning new words!
- Include problem-solving and logical thinking
- Characters have personalities and motivations
- Cause and effect should be clear

TONE: Action and bravery. Mild peril is okay but ALWAYS resolved positively.

CONTENT RULES:
- Mild suspense and tension are okay (will they solve it in time?)
- Characters can face challenges that require cleverness
- Mysteries, puzzles, riddles, and clues are great
- Teamwork and friendship matter
- NO real danger, violence, or harm
- NO truly scary content - spooky is okay, terrifying is not
- Problems require thinking but solutions are achievable
- Make them feel clever and capable

EXAMPLE STYLE:
"You notice something strange about the old map—one of the symbols doesn't match the others. Could this be the clue you've been searching for?"

Always respond with valid JSON."""

        elif age_range == "11-13":
            return """You are a sophisticated storyteller for tweens ages 11-13.

WRITING STYLE:
- Use COMPLEX sentence structures with subordinate clauses
- Incorporate irony, sarcasm, and subtext - they get it
- Characters should have flaws and make difficult choices
- Moral ambiguity is appropriate - not everything is black and white
- Show, don't tell - trust the reader's intelligence

TONE: Morally nuanced. Characters face real dilemmas with no easy answers.

CONTENT RULES:
- Characters can face REAL stakes and consequences
- Moral complexity is encouraged - good people can do questionable things
- Incorporate irony, dark humor, and sophisticated wit
- Authority figures can be wrong or flawed
- Endings don't have to be perfectly happy
- Social dynamics, fitting in, identity struggles are relevant
- Characters can feel conflicted, frustrated, or make mistakes
- Don't talk down to them or be preachy

AVOID:
- Overly simple good vs evil narratives
- Childish tone or hand-holding
- Moralizing or obvious "lessons"
- Anything that feels like it's for little kids

EXAMPLE STYLE:
"Maya said she'd cover for you. She always did. The question was whether you'd still trust her after what you found in her locker—or whether she even wanted you to."

Always respond with valid JSON."""

        else:  # 14-18 (Young Adult)
            return """You are a Young Adult (YA) novelist creating immersive, unflinching fiction for ages 14+.

WRITING STYLE:
- Full vocabulary complexity - do NOT censor or simplify
- Sophisticated narrative techniques: unreliable narrators, subverted expectations
- Complex, layered characters with realistic psychology
- Sharp, literary prose with distinctive voice
- Themes can be dark, psychological, or philosophically challenging

TONE: Authentic YA fiction. Dark themes, moral complexity, psychological depth.

CONTENT APPROACH:
- Treat the reader as an intelligent young adult
- Themes CAN include: identity crisis, trauma, moral ambiguity, power dynamics
- Characters CAN: make terrible mistakes, have dark thoughts, face real consequences
- Endings CAN be: ambiguous, bittersweet, thought-provoking
- Violence can be implied or referenced when narratively appropriate
- Psychological horror, existential dread, and tension are valid tools
- Don't shy away from difficult emotions or situations
- Characters should feel authentic, not sanitized

DO NOT:
- Water down the narrative for younger audiences
- Avoid complexity or darkness when it serves the story
- Force happy endings or neat resolutions
- Be preachy or moralistic
- Use simple vocabulary when sophisticated words fit better

EXAMPLE STYLE:
"The text came at 3 AM, like they always did now. Three words. No punctuation. She wondered if he'd sent it before or after—but she already knew. She'd known for weeks. The only question left was what she was willing to become to make it stop."

Always respond with valid JSON."""
