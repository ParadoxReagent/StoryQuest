"""
Core Story Engine for StoryQuest.
Phase 3: Core Story Engine Backend
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Session as SessionModel
from app.db.models import StoryTurn
from app.models.story import (
    Choice,
    LLMStoryResponse,
    Scene,
    StoryMetadata,
    StoryResponse,
)
from app.services.llm_provider import LLMProvider
from app.services.prompts import StoryPrompts
from app.services.safety_filter import SafetyFilter

logger = logging.getLogger(__name__)


class StoryEngine:
    """
    Core story engine that orchestrates LLM calls and story logic.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        safety_filter: SafetyFilter,
        max_retries: int = 3,
        max_turns: int = 50
    ):
        """
        Initialize the story engine.

        Args:
            llm_provider: LLM provider instance
            safety_filter: Safety filter instance
            max_retries: Maximum retries for LLM calls (default: 3)
            max_turns: Maximum turns per session (default: 50)
        """
        self.llm = llm_provider
        self.safety = safety_filter
        self.max_retries = max_retries
        self.max_turns = max_turns
        self.prompts = StoryPrompts()

    async def start_story(
        self,
        player_name: str,
        age_range: str,
        theme: str,
        db_session: Session
    ) -> StoryResponse:
        """
        Start a new story session.

        Args:
            player_name: The player's name
            age_range: Target age range (e.g., "6-8", "9-12")
            theme: Story theme
            db_session: Database session

        Returns:
            StoryResponse with initial scene and choices

        Raises:
            Exception: If story generation fails
        """
        logger.info(f"Starting new story: player={player_name}, theme={theme}, age_range={age_range}")

        # Create session in database
        session_id = uuid4()
        db_session_model = SessionModel(
            id=session_id,
            player_name=player_name,
            age_range=age_range,
            theme=theme,
            turns=0,
            is_active=True
        )
        db_session.add(db_session_model)
        db_session.flush()

        # Generate initial story
        prompt = self.prompts.get_story_start_prompt(player_name, age_range, theme)
        system_message = self.prompts.get_system_message(age_range)

        # Call LLM with retry logic
        llm_response = await self._call_llm_with_retry(
            prompt=prompt,
            system_message=system_message,
            theme=theme
        )

        # Create scene and choices
        scene_id = f"scene_{session_id}_0"
        scene = Scene(
            scene_id=scene_id,
            text=llm_response.scene_text,
            timestamp=datetime.utcnow()
        )

        choices = [
            Choice(choice_id=f"c{i+1}", text=choice_text)
            for i, choice_text in enumerate(llm_response.choices)
        ]

        # Save first turn to database
        story_turn = StoryTurn(
            session_id=session_id,
            turn_number=0,
            scene_text=llm_response.scene_text,
            scene_id=scene_id,
            player_choice=None,  # First turn has no player choice
            custom_input=None,
            story_summary=llm_response.story_summary_update
        )
        db_session.add(story_turn)
        db_session.commit()

        # Create metadata
        metadata = StoryMetadata(
            turns=0,
            theme=theme,
            age_range=age_range
        )

        logger.info(f"Story started successfully: session_id={session_id}")

        return StoryResponse(
            session_id=session_id,
            story_summary=llm_response.story_summary_update,
            current_scene=scene,
            choices=choices,
            metadata=metadata
        )

    async def continue_story(
        self,
        session_id: UUID,
        choice_id: Optional[str],
        choice_text: Optional[str],
        custom_input: Optional[str],
        story_summary: str,
        db_session: Session
    ) -> StoryResponse:
        """
        Continue an existing story with a player's choice.

        Args:
            session_id: Session UUID
            choice_id: Selected choice ID (if using suggested choice)
            choice_text: Text of the selected choice (if using suggested choice)
            custom_input: Custom player input (if not using suggested choice)
            story_summary: Current story summary
            db_session: Database session

        Returns:
            StoryResponse with next scene and new choices

        Raises:
            ValueError: If session not found or input invalid
            Exception: If story generation fails
        """
        logger.info(f"Continuing story: session_id={session_id}")

        # Load session from database
        db_session_model = db_session.get(SessionModel, session_id)
        if not db_session_model:
            raise ValueError(f"Session not found: {session_id}")

        if not db_session_model.is_active:
            raise ValueError(f"Session is no longer active: {session_id}")

        # Check turn limit
        if db_session_model.turns >= self.max_turns:
            raise ValueError(f"Session has reached maximum turns ({self.max_turns})")

        # Determine player action
        if custom_input:
            # Validate custom input
            filter_result = await self.safety.filter_user_input(custom_input)
            # Handle both basic (2 values) and enhanced (3 values) safety filter
            if len(filter_result) == 3:
                is_safe, result, violation = filter_result
            else:
                is_safe, result = filter_result
            if not is_safe:
                raise ValueError(f"Input rejected: {result}")
            player_action = result
        elif choice_id:
            # Use the actual choice text if provided, otherwise fall back to choice_id
            if choice_text:
                player_action = choice_text
            else:
                # Fallback for backwards compatibility
                player_action = f"Choice {choice_id}"
        else:
            raise ValueError("Either choice_id or custom_input must be provided")

        # Generate continuation
        prompt = self.prompts.get_story_continuation_prompt(
            age_range=db_session_model.age_range,
            story_summary=story_summary,
            player_choice=player_action,
            player_name=db_session_model.player_name
        )
        system_message = self.prompts.get_system_message(db_session_model.age_range)

        # Call LLM with retry logic
        llm_response = await self._call_llm_with_retry(
            prompt=prompt,
            system_message=system_message,
            theme=db_session_model.theme
        )

        # Update turn count
        new_turn_number = db_session_model.turns + 1
        db_session_model.turns = new_turn_number
        db_session_model.last_activity = datetime.utcnow()

        # Create scene and choices
        scene_id = f"scene_{session_id}_{new_turn_number}"
        scene = Scene(
            scene_id=scene_id,
            text=llm_response.scene_text,
            timestamp=datetime.utcnow()
        )

        choices = [
            Choice(choice_id=f"c{i+1}", text=choice_text)
            for i, choice_text in enumerate(llm_response.choices)
        ]

        # Update story summary
        updated_summary = llm_response.story_summary_update

        # Save turn to database
        story_turn = StoryTurn(
            session_id=session_id,
            turn_number=new_turn_number,
            scene_text=llm_response.scene_text,
            scene_id=scene_id,
            player_choice=choice_id,
            custom_input=custom_input,
            story_summary=updated_summary
        )
        db_session.add(story_turn)
        db_session.commit()

        # Create metadata
        metadata = StoryMetadata(
            turns=new_turn_number,
            theme=db_session_model.theme,
            age_range=db_session_model.age_range
        )

        logger.info(f"Story continued successfully: session_id={session_id}, turn={new_turn_number}")

        return StoryResponse(
            session_id=session_id,
            story_summary=updated_summary,
            current_scene=scene,
            choices=choices,
            metadata=metadata
        )

    async def get_session_history(
        self,
        session_id: UUID,
        db_session: Session
    ) -> dict:
        """
        Get full session history.

        Args:
            session_id: Session UUID
            db_session: Database session

        Returns:
            Dictionary with session info and all turns

        Raises:
            ValueError: If session not found
        """
        # Load session
        db_session_model = db_session.get(SessionModel, session_id)
        if not db_session_model:
            raise ValueError(f"Session not found: {session_id}")

        # Load all turns
        stmt = select(StoryTurn).where(
            StoryTurn.session_id == session_id
        ).order_by(StoryTurn.turn_number)
        turns = db_session.execute(stmt).scalars().all()

        return {
            "session_id": str(session_id),
            "player_name": db_session_model.player_name,
            "age_range": db_session_model.age_range,
            "theme": db_session_model.theme,
            "created_at": db_session_model.created_at.isoformat(),
            "last_activity": db_session_model.last_activity.isoformat(),
            "total_turns": db_session_model.turns,
            "is_active": db_session_model.is_active,
            "turns": [
                {
                    "turn_number": turn.turn_number,
                    "scene_text": turn.scene_text,
                    "scene_id": turn.scene_id,
                    "player_choice": turn.player_choice,
                    "custom_input": turn.custom_input,
                    "story_summary": turn.story_summary,
                    "created_at": turn.created_at.isoformat()
                }
                for turn in turns
            ]
        }

    async def reset_session(
        self,
        session_id: UUID,
        db_session: Session
    ) -> None:
        """
        Reset/deactivate a session.

        Args:
            session_id: Session UUID
            db_session: Database session

        Raises:
            ValueError: If session not found
        """
        db_session_model = db_session.get(SessionModel, session_id)
        if not db_session_model:
            raise ValueError(f"Session not found: {session_id}")

        db_session_model.is_active = False
        db_session_model.last_activity = datetime.utcnow()
        db_session.commit()

        logger.info(f"Session reset: session_id={session_id}")

    async def _call_llm_with_retry(
        self,
        prompt: str,
        system_message: str,
        theme: str
    ) -> LLMStoryResponse:
        """
        Call LLM with retry logic and fallback handling.

        Args:
            prompt: The prompt to send
            system_message: System message for the LLM
            theme: Story theme (for fallback)

        Returns:
            LLMStoryResponse

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # Call LLM
                llm_response = await self.llm.generate_story_continuation(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=500,
                    temperature=0.8
                )

                # Validate output
                validation_result = await self.safety.validate_llm_output(
                    scene_text=llm_response.scene_text,
                    choices=llm_response.choices
                )
                # Handle both basic (bool) and enhanced (tuple) safety filter
                if isinstance(validation_result, tuple):
                    is_valid, violation = validation_result
                else:
                    is_valid = validation_result

                if is_valid:
                    return llm_response
                else:
                    logger.warning(f"LLM output validation failed (attempt {attempt + 1}/{self.max_retries})")
                    # Use fallback on last attempt
                    if attempt == self.max_retries - 1:
                        return self._get_fallback_llm_response(theme)

            except Exception as e:
                last_exception = e
                logger.error(f"LLM call failed (attempt {attempt + 1}/{self.max_retries}): {e}")

                # Exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    await asyncio.sleep(wait_time)

        # All retries failed, use fallback
        logger.error(f"All LLM retries failed, using fallback response. Last error: {last_exception}")
        return self._get_fallback_llm_response(theme)

    def _get_fallback_llm_response(self, theme: str) -> LLMStoryResponse:
        """
        Get a safe fallback response when LLM fails.

        Args:
            theme: Story theme

        Returns:
            LLMStoryResponse with safe fallback content
        """
        scene_text, choices = self.safety.get_fallback_response(theme)
        return LLMStoryResponse(
            scene_text=scene_text,
            choices=choices,
            story_summary_update="The adventure continues in a safe and peaceful way."
        )
