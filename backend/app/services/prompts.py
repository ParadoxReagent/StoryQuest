"""
LLM prompt templates for story generation.
Phase 1: Story format & API contract
"""

from typing import Dict


class StoryPrompts:
    """Template manager for LLM prompts."""

    @staticmethod
    def get_story_continuation_prompt(
        age_range: str,
        story_summary: str,
        player_choice: str,
        player_name: str = "the player"
    ) -> str:
        """
        Generate a prompt for continuing the story.

        Args:
            age_range: Target age range (e.g., "6-8", "9-12")
            story_summary: Summary of the story so far
            player_choice: The action the player chose to take
            player_name: The player's name (default: "the player")

        Returns:
            Formatted prompt string
        """
        return f"""You are a creative, kid-friendly storyteller for children aged {age_range}.

STORY SO FAR:
{story_summary}

PLAYER ACTION:
{player_choice}

RULES:
1. Keep content G-rated: no violence, scary themes, or adult content
2. Write 2-4 sentences describing what happens next
3. Generate exactly 3 fun, age-appropriate choices for what to do next
4. Use playful, encouraging language
5. Include learning opportunities (curiosity, problem-solving, kindness)
6. Make {player_name} feel heroic and capable
7. Keep the story moving forward with interesting developments

Respond in this JSON format:
{{
  "scene_text": "What happens next...",
  "choices": [
    "Choice 1",
    "Choice 2",
    "Choice 3"
  ],
  "story_summary_update": "Brief update to story summary"
}}"""

    @staticmethod
    def get_story_start_prompt(
        player_name: str,
        age_range: str,
        theme: str
    ) -> str:
        """
        Generate a prompt for starting a new story.

        Args:
            player_name: The player's name
            age_range: Target age range (e.g., "6-8", "9-12")
            theme: Story theme (e.g., "space_adventure", "magical_forest")

        Returns:
            Formatted prompt string
        """
        theme_descriptions = {
            "space_adventure": "a thrilling space exploration adventure with planets, stars, and friendly aliens",
            "magical_forest": "a whimsical journey through an enchanted forest with magical creatures",
            "underwater_quest": "an exciting underwater adventure with sea creatures and hidden treasures",
            "dinosaur_discovery": "a prehistoric adventure with friendly dinosaurs and ancient mysteries",
            "castle_quest": "a medieval adventure in a grand castle with knights and dragons",
            "robot_city": "a futuristic city adventure with helpful robots and amazing technology",
        }

        theme_desc = theme_descriptions.get(
            theme,
            "an exciting adventure filled with wonder and discovery"
        )

        return f"""You are a creative, kid-friendly storyteller for children aged {age_range}.

Create the opening scene for a brand new story about {player_name}, who is about to begin {theme_desc}.

RULES:
1. Keep content G-rated: no violence, scary themes, or adult content
2. Write an exciting opening (2-4 sentences) that introduces the setting and situation
3. Generate exactly 3 fun, age-appropriate choices for what to do first
4. Use playful, encouraging language
5. Make {player_name} the hero of the story
6. Create a sense of wonder and excitement
7. Theme: {theme}

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
Your stories are always:
- Safe and age-appropriate (G-rated)
- Encouraging and positive
- Educational while being fun
- Free from violence, scary content, or adult themes
- Focused on kindness, curiosity, and problem-solving

Always respond with valid JSON in the exact format requested."""
