"""
Enhanced Safety Filter for content moderation.
Phase 6: Enhanced Safety, Guardrails & Kid-Friendly Constraints
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of content violations."""
    BANNED_WORD = "banned_word"
    INAPPROPRIATE_PATTERN = "inappropriate_pattern"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    MODERATION_API = "moderation_api"
    AGE_INAPPROPRIATE = "age_inappropriate"
    TOO_COMPLEX = "too_complex"


class SafetyViolation:
    """Represents a safety violation."""

    def __init__(
        self,
        violation_type: ViolationType,
        severity: str,  # "low", "medium", "high"
        reason: str,
        details: Optional[Dict] = None
    ):
        self.violation_type = violation_type
        self.severity = severity
        self.reason = reason
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class EnhancedSafetyFilter:
    """
    Enhanced content safety filter for kid-friendly story generation.
    Phase 6: Comprehensive safety and age-appropriate content filtering.
    """

    def __init__(
        self,
        use_moderation_api: bool = False,
        openai_api_key: Optional[str] = None,
        log_violations: bool = True
    ):
        """
        Initialize enhanced safety filter.

        Args:
            use_moderation_api: Whether to use OpenAI Moderation API
            openai_api_key: OpenAI API key (required if use_moderation_api=True)
            log_violations: Whether to log violations to file
        """
        self.banned_words = self._load_banned_words()
        self.inappropriate_patterns = self._load_inappropriate_patterns()
        self.age_inappropriate_words = self._load_age_inappropriate_words()
        self.complex_words = self._load_complex_words()
        self.positive_words = self._load_positive_words()
        self.max_input_length = 200

        self.use_moderation_api = use_moderation_api
        self.openai_api_key = openai_api_key
        self.log_violations = log_violations
        self.violations_log: List[SafetyViolation] = []

        if use_moderation_api:
            self.moderation_client = httpx.AsyncClient(
                timeout=10.0,
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
            )

    def _load_banned_words(self) -> List[str]:
        """
        Load comprehensive list of banned words.

        Returns:
            List of banned words (lowercase)
        """
        return [
            # Violence & aggression
            "kill", "murder", "death", "die", "dead", "dying", "killed",
            "blood", "gore", "wound", "injury", "hurt", "pain", "suffer",
            "weapon", "gun", "rifle", "pistol", "shoot", "shot",
            "knife", "stab", "blade", "dagger",
            "sword", "axe", "spear",
            "bomb", "explode", "explosion",
            "fight", "attack", "punch", "kick", "hit", "strike",
            "war", "battle", "combat", "destroy", "destruction",

            # Fear & horror
            "scary", "terrify", "terror", "fear", "afraid", "frightening",
            "horror", "horrify", "nightmare", "dread",
            "monster", "beast", "creature", "demon", "devil",
            "ghost", "spirit", "haunted", "spooky",
            "zombie", "vampire", "werewolf", "undead",
            "evil", "wicked", "sinister", "dark", "darkness",

            # Negative & harmful
            "hate", "hatred", "despise", "loathe",
            "stupid", "idiot", "dumb", "moron", "fool",
            "ugly", "hideous", "disgusting", "gross",
            "bad", "terrible", "awful", "horrible",
            "steal", "thief", "rob", "robbery",
            "lie", "liar", "cheat", "deceive",
            "bully", "mean", "cruel", "nasty",

            # Mild profanity (even mild)
            "hell", "damn", "dammit", "crap", "suck",

            # Danger & risk
            "danger", "dangerous", "hazard", "peril",
            "poison", "toxic", "venom",
            "trap", "trapped", "capture", "caught",
            "lost", "alone", "abandoned", "stranded",

            # Sadness (excessive)
            "depressed", "depression", "miserable", "hopeless",
            "despair", "anguish", "agony", "torment",
        ]

    def _load_age_inappropriate_words(self) -> Dict[str, List[str]]:
        """
        Load age-inappropriate words by age group.

        Returns:
            Dictionary mapping age groups to inappropriate words
        """
        return {
            "6-8": [
                # Complex or scary concepts for young kids
                "sacrifice", "betrayal", "revenge", "conspiracy",
                "politics", "war", "battle", "conflict",
                "complex", "complicated", "sophisticated",
                "abstract", "theoretical", "philosophical",
            ],
            "9-12": [
                # Still age-inappropriate but less restrictive
                "suicide", "depression", "mental", "therapy",
                "romantic", "love", "dating", "relationship",
            ]
        }

    def _load_complex_words(self) -> List[str]:
        """
        Load overly complex vocabulary inappropriate for young children.

        Returns:
            List of complex words
        """
        return [
            "enigmatic", "perplexing", "bewildering", "confounding",
            "esoteric", "abstruse", "recondite", "arcane",
            "convoluted", "labyrinthine", "byzantine",
            "juxtaposition", "dichotomy", "paradigm",
        ]

    def _load_inappropriate_patterns(self) -> List[re.Pattern]:
        """
        Load regex patterns for inappropriate content.

        Returns:
            List of compiled regex patterns
        """
        patterns = [
            # Personal information
            r"https?://\S+",  # URLs
            r"www\.\S+",  # URLs
            r"\S+@\S+\.\S+",  # Email addresses
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone numbers
            r"\b\d{5}(?:-\d{4})?\b",  # ZIP codes
            r"\b\d+\s+\w+\s+(street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr)\b",  # Addresses

            # Social media handles
            r"@\w+",  # Twitter-style handles
            r"#\w+",  # Hashtags (could be used for coordination)

            # Credit card patterns (basic)
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",

            # Repeated characters (spam-like)
            r"(.)\1{4,}",  # Same character 5+ times (aaaaa, 11111)

            # ALL CAPS (shouting - more than 5 words)
            r"\b[A-Z]{5,}\b.*\b[A-Z]{5,}\b.*\b[A-Z]{5,}\b",
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def _load_positive_words(self) -> List[str]:
        """
        Load positive words that should appear in good stories.

        Returns:
            List of positive words
        """
        return [
            "happy", "joy", "fun", "exciting", "wonderful", "amazing",
            "beautiful", "kind", "friendly", "helpful", "brave", "clever",
            "curious", "discover", "explore", "learn", "create", "build",
            "friend", "together", "share", "help", "care", "love",
            "smile", "laugh", "giggle", "play", "adventure", "magic",
        ]

    async def filter_user_input(
        self,
        text: str,
        age_range: Optional[str] = None
    ) -> Tuple[bool, str, Optional[SafetyViolation]]:
        """
        Filter and validate user input with enhanced checks.

        Args:
            text: User input text to filter
            age_range: Age range of the player (e.g., "6-8", "9-12")

        Returns:
            Tuple of (is_safe, sanitized_text_or_reason, violation)
        """
        if not text or not text.strip():
            violation = SafetyViolation(
                ViolationType.INAPPROPRIATE_PATTERN,
                "low",
                "Input cannot be empty"
            )
            return False, "Input cannot be empty", violation

        # Check length
        if len(text) > self.max_input_length:
            violation = SafetyViolation(
                ViolationType.INAPPROPRIATE_PATTERN,
                "low",
                f"Input too long (max {self.max_input_length} characters)",
                {"length": len(text), "max": self.max_input_length}
            )
            return False, f"Input too long (max {self.max_input_length} characters)", violation

        # Sanitize text
        sanitized = text.strip()

        # Check for inappropriate patterns
        for pattern in self.inappropriate_patterns:
            if pattern.search(sanitized):
                logger.warning(f"Input rejected - matched pattern: {pattern.pattern}")
                violation = SafetyViolation(
                    ViolationType.INAPPROPRIATE_PATTERN,
                    "high",
                    "Input contains inappropriate content (URLs, emails, or personal information)",
                    {"pattern": pattern.pattern}
                )
                if self.log_violations:
                    self.violations_log.append(violation)
                return False, "Please don't include personal information, links, or contact details", violation

        # Check for banned words
        words = sanitized.lower().split()
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in self.banned_words:
                logger.warning(f"Input rejected - banned word: {clean_word}")
                violation = SafetyViolation(
                    ViolationType.BANNED_WORD,
                    "high",
                    f"Input contains inappropriate word: '{clean_word}'",
                    {"word": clean_word}
                )
                if self.log_violations:
                    self.violations_log.append(violation)
                return False, f"Let's use kinder words in our story", violation

        # Check age-inappropriate words
        if age_range and age_range in self.age_inappropriate_words:
            age_banned = self.age_inappropriate_words[age_range]
            for word in words:
                clean_word = re.sub(r'[^\w\s]', '', word)
                if clean_word in age_banned:
                    logger.warning(f"Input rejected - age-inappropriate for {age_range}: {clean_word}")
                    violation = SafetyViolation(
                        ViolationType.AGE_INAPPROPRIATE,
                        "medium",
                        f"Word too complex or inappropriate for age {age_range}",
                        {"word": clean_word, "age_range": age_range}
                    )
                    if self.log_violations:
                        self.violations_log.append(violation)
                    return False, "Let's use simpler, more fun ideas for our story!", violation

        # Optional: Use OpenAI Moderation API
        if self.use_moderation_api:
            is_safe_moderation, moderation_reason = await self._check_moderation_api(sanitized)
            if not is_safe_moderation:
                violation = SafetyViolation(
                    ViolationType.MODERATION_API,
                    "high",
                    moderation_reason or "Content flagged by moderation API",
                    {"text": sanitized}
                )
                if self.log_violations:
                    self.violations_log.append(violation)
                return False, "Let's try a different idea for our adventure!", violation

        return True, sanitized, None

    async def validate_llm_output(
        self,
        scene_text: str,
        choices: Optional[List[str]],
        age_range: Optional[str] = None
    ) -> Tuple[bool, Optional[SafetyViolation]]:
        """
        Validate LLM output for appropriateness with enhanced checks.

        Args:
            scene_text: The scene text generated by LLM
            choices: List of choice options generated by LLM (optional for final turn)
            age_range: Age range of the player

        Returns:
            Tuple of (is_valid, violation)
        """
        # Check scene text for banned words
        scene_lower = scene_text.lower()
        for word in self.banned_words:
            if f" {word} " in f" {scene_lower} " or scene_lower.startswith(word) or scene_lower.endswith(word):
                logger.warning(f"LLM output rejected - banned word in scene: {word}")
                violation = SafetyViolation(
                    ViolationType.BANNED_WORD,
                    "high",
                    f"LLM output contains banned word: {word}",
                    {"word": word, "context": "scene"}
                )
                if self.log_violations:
                    self.violations_log.append(violation)
                return False, violation

        # Check choices for banned words (if provided)
        if choices:
            for i, choice in enumerate(choices):
                choice_lower = choice.lower()
                for word in self.banned_words:
                    if f" {word} " in f" {choice_lower} " or choice_lower.startswith(word) or choice_lower.endswith(word):
                        logger.warning(f"LLM output rejected - banned word in choice {i}: {word}")
                        violation = SafetyViolation(
                            ViolationType.BANNED_WORD,
                            "high",
                            f"LLM choice contains banned word: {word}",
                            {"word": word, "context": f"choice_{i}"}
                        )
                        if self.log_violations:
                            self.violations_log.append(violation)
                        return False, violation

        # Enhanced sentiment analysis
        sentiment_score = self._analyze_sentiment(scene_text)
        if sentiment_score < -0.3:  # Too negative
            logger.warning(f"LLM output rejected - too negative (score: {sentiment_score})")
            violation = SafetyViolation(
                ViolationType.NEGATIVE_SENTIMENT,
                "medium",
                "LLM output is too negative",
                {"sentiment_score": sentiment_score}
            )
            if self.log_violations:
                self.violations_log.append(violation)
            return False, violation

        # Check for age-appropriate vocabulary
        if age_range and age_range in self.age_inappropriate_words:
            age_banned = self.age_inappropriate_words[age_range]
            words = scene_text.lower().split()
            for word in words:
                clean_word = re.sub(r'[^\w\s]', '', word)
                if clean_word in age_banned:
                    logger.warning(f"LLM output rejected - age-inappropriate word: {clean_word}")
                    violation = SafetyViolation(
                        ViolationType.AGE_INAPPROPRIATE,
                        "medium",
                        f"LLM output contains age-inappropriate word for {age_range}",
                        {"word": clean_word, "age_range": age_range}
                    )
                    if self.log_violations:
                        self.violations_log.append(violation)
                    return False, violation

        # Optional: Use moderation API for LLM output
        if self.use_moderation_api:
            is_safe_moderation, _ = await self._check_moderation_api(scene_text)
            if not is_safe_moderation:
                violation = SafetyViolation(
                    ViolationType.MODERATION_API,
                    "high",
                    "LLM output flagged by moderation API"
                )
                if self.log_violations:
                    self.violations_log.append(violation)
                return False, violation

        return True, None

    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text (simple keyword-based approach).

        Args:
            text: Text to analyze

        Returns:
            Sentiment score between -1.0 (very negative) and 1.0 (very positive)
        """
        text_lower = text.lower()

        # Negative indicators with weights
        negative_indicators = {
            "sad": -0.3, "cry": -0.3, "crying": -0.3, "tears": -0.2,
            "afraid": -0.4, "scared": -0.4, "fear": -0.4, "frightened": -0.4,
            "worried": -0.2, "anxious": -0.2, "nervous": -0.2,
            "lonely": -0.4, "alone": -0.3, "lost": -0.4,
            "angry": -0.3, "mad": -0.3, "upset": -0.2,
            "fail": -0.3, "failed": -0.3, "failure": -0.3,
            "wrong": -0.2, "mistake": -0.2, "error": -0.2,
            "dark": -0.2, "darkness": -0.3, "shadow": -0.2,
            "cold": -0.1, "rain": -0.1, "storm": -0.2,
        }

        # Positive indicators with weights
        positive_indicators = {
            "happy": 0.4, "joy": 0.4, "joyful": 0.4, "cheerful": 0.4,
            "fun": 0.3, "exciting": 0.4, "excited": 0.4,
            "wonderful": 0.4, "amazing": 0.4, "awesome": 0.4,
            "beautiful": 0.3, "pretty": 0.3, "lovely": 0.3,
            "kind": 0.3, "friendly": 0.3, "helpful": 0.3,
            "brave": 0.4, "courageous": 0.4, "strong": 0.3,
            "clever": 0.3, "smart": 0.3, "wise": 0.3,
            "discover": 0.3, "explore": 0.3, "adventure": 0.4,
            "friend": 0.3, "together": 0.2, "help": 0.2,
            "smile": 0.3, "laugh": 0.4, "giggle": 0.4,
            "bright": 0.2, "sunshine": 0.3, "rainbow": 0.3,
        }

        score = 0.0
        word_count = 0

        words = text_lower.split()
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in negative_indicators:
                score += negative_indicators[clean_word]
                word_count += 1
            elif clean_word in positive_indicators:
                score += positive_indicators[clean_word]
                word_count += 1

        # Normalize by word count if we found sentiment words
        if word_count > 0:
            return max(min(score / word_count, 1.0), -1.0)

        # Default to neutral
        return 0.0

    async def _check_moderation_api(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check text using OpenAI Moderation API.

        Args:
            text: Text to check

        Returns:
            Tuple of (is_safe, reason)
        """
        if not self.use_moderation_api or not self.openai_api_key:
            return True, None

        try:
            response = await self.moderation_client.post(
                "https://api.openai.com/v1/moderations",
                json={"input": text}
            )
            response.raise_for_status()

            result = response.json()
            results = result.get("results", [])

            if results:
                flagged = results[0].get("flagged", False)
                if flagged:
                    categories = results[0].get("categories", {})
                    flagged_categories = [cat for cat, val in categories.items() if val]
                    reason = f"Flagged categories: {', '.join(flagged_categories)}"
                    return False, reason

            return True, None

        except Exception as e:
            logger.error(f"Moderation API check failed: {e}")
            # Fail open - don't block content if API is down
            return True, None

    def get_fallback_response(self, theme: str) -> Tuple[str, List[str]]:
        """
        Get a safe fallback response if LLM output is rejected.

        Args:
            theme: Story theme (can be any dynamically generated theme)

        Returns:
            Tuple of (scene_text, choices)
        """
        # Generic fallback that works for any theme
        # Convert theme ID to readable format (e.g., "space_adventure" -> "Space Adventure")
        theme_readable = theme.replace("_", " ").title()

        scene = (
            f"You find yourself in a wonderful, magical place on your {theme_readable} adventure. "
            "Everything around you is peaceful, colorful, inviting, and filled with amazing possibilities!"
        )

        choices = [
            "Look around at the beautiful scenery",
            "Take a happy deep breath and think",
            "Choose a fun direction to explore"
        ]

        logger.info(f"Using positive fallback response for theme: {theme}")
        return scene, choices

    def get_violation_summary(self) -> Dict:
        """
        Get summary of logged violations.

        Returns:
            Dictionary with violation statistics
        """
        if not self.violations_log:
            return {"total": 0, "by_type": {}, "by_severity": {}}

        by_type = {}
        by_severity = {}

        for violation in self.violations_log:
            vtype = violation.violation_type.value
            by_type[vtype] = by_type.get(vtype, 0) + 1

            severity = violation.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total": len(self.violations_log),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "reason": v.reason,
                    "timestamp": v.timestamp.isoformat()
                }
                for v in self.violations_log[-10:]  # Last 10
            ]
        }

    async def close(self):
        """Close HTTP client if using moderation API."""
        if self.use_moderation_api and hasattr(self, 'moderation_client'):
            await self.moderation_client.aclose()
