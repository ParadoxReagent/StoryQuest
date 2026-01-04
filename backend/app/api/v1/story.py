"""
Story API endpoints.
Phase 6: Enhanced with rate limiting and safety features
"""

import json
import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import get_config
from app.db.database import get_db_session
from app.db.models import Session as SessionModel
from app.models.story import (
    ContinueStoryRequest,
    GenerateThemesRequest,
    GenerateThemesResponse,
    StartStoryRequest,
    StoryResponse,
    ThemeOption,
)
from app.services.llm_factory import create_llm_provider
from app.services.prompts import StoryPrompts
from app.services.safety_filter import SafetyFilter
from app.services.safety_filter_enhanced import EnhancedSafetyFilter
from app.services.story_engine import StoryEngine, compute_max_turns
from app.services.rate_limiter import get_rate_limiter, RateLimitExceeded

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/story", tags=["story"])


def get_story_engine() -> StoryEngine:
    """
    Dependency for getting StoryEngine instance.
    Phase 6: Uses enhanced safety filter based on configuration.

    Returns:
        StoryEngine instance
    """
    config = get_config()
    llm_provider = create_llm_provider(config)

    # Use enhanced safety filter if enabled in config
    if config.safety.use_enhanced_filter:
        # Get OpenAI API key from settings if moderation API is enabled
        openai_key = None
        if config.safety.use_moderation_api:
            try:
                from app.config import Settings
                settings = Settings()
                openai_key = settings.OPENAI_API_KEY
            except Exception as e:
                logger.warning(f"Could not load OpenAI API key for moderation: {e}")

        safety_filter = EnhancedSafetyFilter(
            use_moderation_api=config.safety.use_moderation_api,
            openai_api_key=openai_key,
            log_violations=config.safety.log_violations
        )
    else:
        # Use basic safety filter
        safety_filter = SafetyFilter()

    return StoryEngine(
        llm_provider=llm_provider,
        safety_filter=safety_filter,
        max_retries=3,
        max_turns=config.safety.max_turns_per_session
    )


@router.post("/start", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def start_story(
    http_request: Request,
    request: StartStoryRequest,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> StoryResponse:
    """
    Start a new story session.
    Phase 6: Includes rate limiting to prevent abuse.

    Args:
        http_request: HTTP request (for rate limiting)
        request: Story initialization parameters (player_name, age_range, theme)
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        StoryResponse with initial scene and choices
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)

        # Check start story rate limit
        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(client_ip)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on start_story")
            raise RateLimitExceeded(retry_after)

        # Check general IP rate limit
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "start_story")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    try:
        logger.info(f"Starting story for player: {request.player_name}, theme: {request.theme}")
        response = await engine.start_story(
            player_name=request.player_name,
            age_range=request.age_range,
            theme=request.theme,
            db_session=db
        )
        return response
    except ValueError as e:
        logger.error(f"Validation error starting story: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting story: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start story. Please try again."
        )


@router.post("/continue", response_model=StoryResponse)
async def continue_story(
    http_request: Request,
    request: ContinueStoryRequest,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> StoryResponse:
    """
    Continue an existing story with a player's choice.
    Phase 6: Includes rate limiting to prevent abuse.

    Args:
        http_request: HTTP request (for rate limiting)
        request: Session ID, choice, and current story state
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        StoryResponse with next scene and new choices
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)
        session_id_str = str(request.session_id)

        # Check session rate limit
        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id_str, "continue")
        if not is_allowed:
            logger.warning(f"Session rate limit exceeded for session {session_id_str}")
            raise RateLimitExceeded(retry_after)

        # If custom input, check stricter rate limit
        if request.custom_input:
            is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id_str)
            if not is_allowed:
                logger.warning(f"Custom input rate limit exceeded for session {session_id_str}")
                raise RateLimitExceeded(retry_after)

        # Check general IP rate limit
        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "continue")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    try:
        logger.info(f"Continuing story for session: {request.session_id}")
        response = await engine.continue_story(
            session_id=request.session_id,
            choice_id=request.choice_id,
            choice_text=request.choice_text,
            custom_input=request.custom_input,
            story_summary=request.story_summary,
            db_session=db
        )
        return response
    except ValueError as e:
        logger.error(f"Validation error continuing story: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error continuing story: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to continue story. Please try again."
        )


@router.post("/start/stream")
async def start_story_stream(
    http_request: Request,
    request: StartStoryRequest,
    db: Session = Depends(get_db_session)
):
    """
    Start a new story session with streaming response.

    Returns Server-Sent Events (SSE) with:
    - Stream of text chunks as they're generated
    - Final event with choices and metadata
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)

        is_allowed, retry_after = rate_limiter.check_start_story_rate_limit(client_ip)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on start_story_stream")
            raise RateLimitExceeded(retry_after)

        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "start_story")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    async def generate_stream():
        """Generate SSE stream for story start."""
        try:
            # Create LLM provider and prompts
            llm_provider = create_llm_provider(config)
            prompts = StoryPrompts()

            # Create session in database
            session_id = uuid4()
            max_turns = compute_max_turns(session_id)
            db_session_model = SessionModel(
                id=session_id,
                player_name=request.player_name,
                age_range=request.age_range,
                theme=request.theme,
                turns=0,
                is_active=True
            )
            db.add(db_session_model)
            db.flush()

            # Generate prompts
            prompt = prompts.get_story_start_prompt(
                request.player_name,
                request.age_range,
                request.theme
            )
            system_message = prompts.get_system_message(request.age_range)

            # Send initial event with session info
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': str(session_id)})}\n\n"

            # Accumulate full response for parsing
            full_response = ""

            # Stream LLM response
            async for chunk in llm_provider.generate_story_continuation_stream(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.8
            ):
                full_response += chunk
                # Send text chunk
                yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"

            # Parse complete response to extract scene_text and choices
            try:
                # Use the concrete provider instance to parse the response
                llm_response = llm_provider._parse_llm_response(full_response)

                # Create choices with generated IDs (matching StoryEngine format)
                choices = [
                    {
                        "choice_id": f"c{i + 1}",
                        "text": choice_text
                    }
                    for i, choice_text in enumerate(llm_response.choices or [])
                ]

                story_summary = llm_response.story_summary_update or ""

                # Generate a scene id consistent with StoryEngine
                scene_id = f"scene_{session_id}_0"

                # Save to database
                from app.db.models import StoryTurn
                turn = StoryTurn(
                    id=uuid4(),
                    session_id=session_id,
                    turn_number=0,
                    scene_text=llm_response.scene_text,
                    scene_id=scene_id,
                    player_choice=None,
                    custom_input=None,
                    story_summary=story_summary
                )
                db.add(turn)
                db_session_model.turns = 0
                db_session_model.updated_at = turn.created_at
                db.commit()

                # Send final event with metadata
                yield f"data: {json.dumps({'type': 'complete', 'choices': choices, 'metadata': {'theme': request.theme, 'age_range': request.age_range, 'turns': 0, 'session_id': str(session_id), 'max_turns': max_turns, 'is_finished': False}, 'scene_text': llm_response.scene_text, 'story_summary': story_summary})}\n\n"

            except Exception as e:
                logger.error(f"Failed to parse streamed response: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to parse story response'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming story start: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/continue/stream")
async def continue_story_stream(
    http_request: Request,
    request: ContinueStoryRequest,
    db: Session = Depends(get_db_session)
):
    """
    Continue an existing story with streaming response.

    Returns Server-Sent Events (SSE) with:
    - Stream of text chunks as they're generated
    - Final event with choices and metadata
    """
    config = get_config()

    # Rate limiting check (if enabled)
    if config.safety.enable_rate_limiting:
        rate_limiter = get_rate_limiter()
        client_ip = rate_limiter.get_client_ip(http_request)
        session_id_str = str(request.session_id)

        is_allowed, retry_after = rate_limiter.check_session_rate_limit(session_id_str, "continue")
        if not is_allowed:
            logger.warning(f"Session rate limit exceeded for session {session_id_str}")
            raise RateLimitExceeded(retry_after)

        if request.custom_input:
            is_allowed, retry_after = rate_limiter.check_custom_input_rate_limit(session_id_str)
            if not is_allowed:
                logger.warning(f"Custom input rate limit exceeded for session {session_id_str}")
                raise RateLimitExceeded(retry_after)

        is_allowed, retry_after = rate_limiter.check_ip_rate_limit(client_ip, "continue")
        if not is_allowed:
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise RateLimitExceeded(retry_after)

    async def generate_stream():
        """Generate SSE stream for story continuation."""
        try:
            # Create LLM provider and prompts
            llm_provider = create_llm_provider(config)
            prompts = StoryPrompts()

            # Load session from database
            from sqlalchemy import select
            stmt = select(SessionModel).where(SessionModel.id == request.session_id)
            result = db.execute(stmt)
            db_session_model = result.scalar_one_or_none()

            if not db_session_model:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
                return

            if not db_session_model.is_active:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session is no longer active'})}\n\n"
                return

            max_turns = compute_max_turns(db_session_model.id)
            next_turn_number = db_session_model.turns + 1
            turns_remaining = max_turns - next_turn_number

            if db_session_model.turns >= max_turns:
                yield f"data: {json.dumps({'type': 'error', 'message': 'This story has already reached its ending.'})}\n\n"
                return

            # Get choice text
            choice_text = request.choice_text if request.choice_text else request.custom_input

            # Generate continuation prompt
            prompt = prompts.get_story_continuation_prompt(
                age_range=db_session_model.age_range,
                story_summary=request.story_summary or "",
                player_choice=choice_text or "",
                player_name=db_session_model.player_name,
                turns_remaining=turns_remaining
            )
            system_message = prompts.get_system_message(db_session_model.age_range)

            # Accumulate full response for parsing
            full_response = ""

            # Stream LLM response
            async for chunk in llm_provider.generate_story_continuation_stream(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.8
            ):
                full_response += chunk
                # Send text chunk
                yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"

            # Parse complete response
            try:
                llm_response = llm_provider._parse_llm_response(full_response)

                # Create choices
                choices = [
                    {
                        "choice_id": f"c{i + 1}",
                        "text": choice_text
                    }
                    for i, choice_text in enumerate(llm_response.choices or [])
                ] if next_turn_number < max_turns and llm_response.choices else []

                new_turn_number = next_turn_number
                scene_id = f"scene_{request.session_id}_{new_turn_number}"
                updated_summary = llm_response.story_summary_update or request.story_summary or ""
                is_finished = new_turn_number >= max_turns

                # Save to database
                from app.db.models import StoryTurn
                turn = StoryTurn(
                    id=uuid4(),
                    session_id=request.session_id,
                    turn_number=new_turn_number,
                    scene_text=llm_response.scene_text,
                    scene_id=scene_id,
                    player_choice=request.choice_id,
                    custom_input=request.custom_input,
                    story_summary=updated_summary
                )
                db.add(turn)
                db_session_model.turns = new_turn_number
                db_session_model.updated_at = turn.created_at
                db_session_model.is_active = not is_finished
                db.commit()

                # Send final event
                yield f"data: {json.dumps({'type': 'complete', 'choices': choices, 'metadata': {'theme': db_session_model.theme, 'age_range': db_session_model.age_range, 'turns': new_turn_number, 'session_id': str(request.session_id), 'max_turns': max_turns, 'is_finished': is_finished}, 'scene_text': llm_response.scene_text, 'story_summary': updated_summary})}\n\n"

            except Exception as e:
                logger.error(f"Failed to parse streamed response: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to parse story response'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming story continuation: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/session/{session_id}", response_model=dict)
async def get_session(
    session_id: UUID,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> dict:
    """
    Retrieve full story history for a session.

    Args:
        session_id: The session UUID to retrieve
        engine: Story engine instance (injected)
        db: Database session (injected)

    Returns:
        Complete session history with all turns
    """
    try:
        logger.info(f"Retrieving session: {session_id}")
        history = await engine.get_session_history(
            session_id=session_id,
            db_session=db
        )
        return history
    except ValueError as e:
        logger.error(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session. Please try again."
        )


@router.post("/generate-themes", response_model=GenerateThemesResponse)
async def generate_themes(
    request: GenerateThemesRequest
) -> GenerateThemesResponse:
    """
    Generate random age-appropriate story themes using LLM.

    Args:
        request: Contains age_range for generating appropriate themes

    Returns:
        GenerateThemesResponse with list of 6 randomly generated themes
    """
    try:
        logger.info(f"Generating themes for age range: {request.age_range}")
        config = get_config()
        llm_provider = create_llm_provider(config)

        # Define color options for the themes
        color_options = [
            "from-indigo-400 to-purple-500",
            "from-green-400 to-emerald-500",
            "from-cyan-400 to-blue-500",
            "from-orange-400 to-red-500",
            "from-yellow-400 to-amber-500",
            "from-pink-400 to-rose-500",
            "from-teal-400 to-cyan-500",
            "from-violet-400 to-fuchsia-500",
        ]

        # Create age-specific prompts with drastically different tones
        age_range = request.age_range

        if age_range == "5-7":
            age_label = "5-7 years old (Early Reader)"
            age_guidance = """
TONE: Wonder, friendship, gentle magic. NO scary elements whatsoever.

DEVELOPMENTAL CONTEXT FOR AGES 5-7:
- Simple, magical thinking - they believe in the impossible
- Love animals, friendly creatures, and nature
- Short attention spans - themes should be immediately engaging
- Need clear heroes and simple conflicts (lost toy, helping a friend)
- Enjoy repetition and familiar scenarios with a twist
- Respond to sensory details (colors, sounds, textures)
- Love being helpers and feeling capable

GOOD THEME TYPES:
- Friendly animal adventures (talking pets, forest friends)
- Simple magical discoveries (finding a magic object)
- Helping scenarios (rescuing a lost creature, making a friend)
- Imaginative play (toys coming alive, pretend adventures)
- Nature exploration (garden adventures, weather magic)

ABSOLUTELY AVOID:
- ANY scary elements, villains, or danger
- Complex mysteries or puzzles
- Abstract concepts
- Long quests with multiple steps"""

            examples = """[
  {{"name": "Puppy's Lost Bone", "description": "Help a friendly puppy find their favorite bone in the sunny backyard!", "emoji": "🐕"}},
  {{"name": "Rainbow Garden", "description": "Plant magical seeds and watch colorful flowers grow and dance!", "emoji": "🌈"}},
  {{"name": "Teddy's Tea Party", "description": "Your stuffed animals come alive for a magical tea party!", "emoji": "🧸"}}
]"""

        elif age_range == "8-10":
            age_label = "8-10 years old (Middle Reader)"
            age_guidance = """
TONE: Action, bravery, teamwork. Mild peril is okay but always resolved positively.

DEVELOPMENTAL CONTEXT FOR AGES 8-10:
- Developing logical thinking and problem-solving skills
- Enjoy figuring things out and feeling clever
- Can follow multi-step plots with cause and effect
- Interested in how things work (science, nature, technology)
- Developing sense of justice and fairness
- Enjoy humor, wordplay, and mild mischief
- Can handle mild tension and suspense (not horror)
- Interested in friendship dynamics and teamwork

GOOD THEME TYPES:
- Mystery and detective stories (solving puzzles, finding clues)
- Inventor/scientist adventures (building things, experiments)
- Sports and competition themes (fair play, teamwork)
- Time travel and history exploration
- Secret societies and hidden worlds
- Rescue missions with clever solutions
- Treasure hunts with riddles

AVOID:
- Themes too babyish (they want to feel mature)
- Romance or relationship drama
- Real-world violence or serious danger
- Horror or genuinely scary content"""

            examples = """[
  {{"name": "Code Breakers Club", "description": "Crack secret codes to uncover a mystery hidden in your school!", "emoji": "🔐"}},
  {{"name": "Dinosaur Time Machine", "description": "Travel back 65 million years to study dinosaurs for a science fair!", "emoji": "🦖"}},
  {{"name": "Storm Chasers Academy", "description": "Join a team of young meteorologists tracking a powerful storm!", "emoji": "🌪️"}}
]"""

        elif age_range == "11-13":
            age_label = "11-13 years old (Tween)"
            age_guidance = """
TONE: Complex, morally nuanced, incorporates irony and sarcasm. Characters face real dilemmas.

DEVELOPMENTAL CONTEXT FOR AGES 11-13:
- Abstract thinking is developing - they appreciate irony, sarcasm, and subtext
- Interested in social dynamics, fitting in, identity
- Can handle moral complexity and characters making difficult choices
- Enjoy stories where they feel smarter than the characters sometimes
- Appreciate humor that's more sophisticated (not just silly)
- Want to feel mature and respected
- Interested in rebellion, questioning authority (in safe contexts)
- Can handle darker themes when handled thoughtfully

GOOD THEME TYPES:
- Dystopian or alternate reality scenarios
- Heist or elaborate scheme stories
- Stories with unreliable narrators or plot twists
- Social commentary wrapped in adventure
- Characters who are flawed but relatable
- Mysteries with real stakes and moral gray areas
- Stories about outcasts or underdogs

AVOID:
- Anything that feels "preachy" or talks down to them
- Overly simple good vs evil narratives
- Childish themes or tone
- Excessive hand-holding in the narrative"""

            examples = """[
  {{"name": "The Algorithm", "description": "A social media AI starts predicting your choices before you make them.", "emoji": "🤖"}},
  {{"name": "Memory Thieves", "description": "Someone is stealing students' memories, and you might be next.", "emoji": "🧠"}},
  {{"name": "The Last Locker", "description": "Your school's oldest locker hasn't been opened in 50 years. Until now.", "emoji": "🔓"}}
]"""

        else:  # 14-18 (Young Adult)
            age_label = "14+ years old (Young Adult)"
            age_guidance = """
TONE: Young Adult (YA) novel style. Themes can be dark, psychological, or morally complex. Do not censor vocabulary complexity.

DEVELOPMENTAL CONTEXT FOR AGES 14+:
- Fully capable of abstract and philosophical thinking
- Interested in identity, purpose, and big life questions
- Can handle complex moral ambiguity and dark themes
- Appreciate sophisticated narrative techniques
- Want authentic, unflinching storytelling
- Interested in psychology, motivation, and what drives people
- Can handle unreliable narrators, time jumps, and complex structure
- Appreciate when stories don't offer easy answers

GOOD THEME TYPES:
- Psychological thrillers and mind-bending narratives
- Stories exploring identity, trauma, or personal growth
- Dark fantasy with real consequences
- Sci-fi that explores ethical dilemmas
- Stories about power, corruption, and resistance
- Complex relationship dynamics (not just romance)
- Narratives that subvert genre expectations
- Stories where the protagonist might be wrong

ENCOURAGED:
- Morally gray characters
- Unflinching look at difficult topics
- Sophisticated vocabulary and complex sentences
- Subverted expectations and genre-bending
- Dark humor and sharp wit"""

            examples = """[
  {{"name": "The Recursion", "description": "You keep waking up on the same day, but each loop reveals a darker truth about yourself.", "emoji": "♾️"}},
  {{"name": "Bone Orchard", "description": "The town's memorial garden grows a new tree for every secret buried there.", "emoji": "🦴"}},
  {{"name": "The Quiet Room", "description": "Patients check into the experimental therapy program. Not all of them check out.", "emoji": "🚪"}}
]"""

        prompt = f"""Generate 6 UNIQUE and CREATIVE story themes for children aged {age_label}.

{age_guidance}

REQUIREMENTS:
- Each theme must be DISTINCTLY DIFFERENT in setting, genre, and activity
- Avoid generic/overused themes (no basic "magical forest" or "space adventure" unless with a unique twist)
- Themes should feel fresh and specific, not vague
- Names should be catchy and memorable (2-4 words)
- Descriptions should be action-oriented and exciting (10-15 words)

DIVERSITY MANDATE:
Generate themes from at least 4 different categories:
- Adventure/Exploration
- Mystery/Discovery
- Creative/Building
- Nature/Animals
- Sports/Games
- Fantasy/Magic
- Science/Invention
- Friendship/Helping

Format as JSON array with 6 objects:
- "name": theme name (Title Case)
- "description": exciting one-sentence description
- "emoji": single representative emoji

Example format (DO NOT USE THESE - create entirely new themes):
{examples}

Generate 6 completely NEW and CREATIVE themes now:"""

        system_message = f"""You are an expert children's storyteller and child development specialist creating themes for {age_label}.
You deeply understand what captures children's imagination at this specific developmental stage.
You create themes that are fresh, specific, and genuinely exciting - never generic or predictable.
You respond ONLY with valid JSON - no other text."""

        # Call LLM to generate themes
        response_text = await llm_provider.generate_raw_json(
            prompt=prompt,
            system_message=system_message,
            max_tokens=800,
            temperature=0.9  # Higher temperature for more creative variety
        )

        # Parse JSON response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                themes_data = json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                raise ValueError("No JSON array found in LLM response")

            # Validate we got 6 themes
            if len(themes_data) < 6:
                raise ValueError(f"Expected 6 themes, got {len(themes_data)}")

            # Create theme options
            themes = []
            for i, theme_data in enumerate(themes_data[:6]):  # Take first 6
                # Create a URL-safe ID from the name
                theme_id = theme_data["name"].lower().replace(" ", "_").replace("'", "")
                # Remove any non-alphanumeric characters except underscores
                theme_id = re.sub(r'[^a-z0-9_]', '', theme_id)

                themes.append(ThemeOption(
                    id=theme_id,
                    name=theme_data["name"],
                    description=theme_data["description"],
                    emoji=theme_data["emoji"],
                    color=color_options[i % len(color_options)]
                ))

            return GenerateThemesResponse(themes=themes)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse LLM theme response: {e}")
            logger.error(f"LLM response was: {response_text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate themes. Please try again."
            )

    except Exception as e:
        logger.error(f"Error generating themes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate themes. Please try again."
        )


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_session(
    session_id: UUID,
    engine: StoryEngine = Depends(get_story_engine),
    db: Session = Depends(get_db_session)
) -> None:
    """
    Reset/abandon a story session.

    Args:
        session_id: The session UUID to reset
        engine: Story engine instance (injected)
        db: Database session (injected)
    """
    try:
        logger.info(f"Resetting session: {session_id}")
        await engine.reset_session(
            session_id=session_id,
            db_session=db
        )
    except ValueError as e:
        logger.error(f"Session not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset session. Please try again."
        )
