# StoryQuest Safety & Content Moderation Guide

## Phase 6: Enhanced Safety, Guardrails & Kid-Friendly Constraints

StoryQuest prioritizes child safety through multiple layers of content moderation and abuse prevention.

## Table of Contents

1. [Overview](#overview)
2. [Safety Features](#safety-features)
3. [Configuration](#configuration)
4. [Content Filtering](#content-filtering)
5. [Rate Limiting](#rate-limiting)
6. [Monitoring & Admin](#monitoring--admin)
7. [Best Practices](#best-practices)

---

## Overview

StoryQuest implements a comprehensive multi-layer safety system designed to ensure all content is G-rated and appropriate for children aged 6-12.

### Safety Principles

1. **Prevention First**: Strong LLM prompts prevent inappropriate content generation
2. **Multi-Layer Defense**: Input validation, output validation, and optional API moderation
3. **Age-Appropriate**: Different content standards for different age groups
4. **Abuse Prevention**: Rate limiting prevents system abuse
5. **Transparency**: All violations are logged for review

---

## Safety Features

### 1. Enhanced Safety Filter (`EnhancedSafetyFilter`)

The enhanced safety filter provides comprehensive content validation:

**Input Validation:**
- Checks for banned words (100+ inappropriate terms)
- Blocks personal information (URLs, emails, phone numbers, addresses)
- Prevents spam patterns (repeated characters, all caps)
- Age-appropriate vocabulary enforcement
- Length limits (max 200 characters)

**Output Validation:**
- Validates LLM-generated content before delivery
- Sentiment analysis (blocks overly negative content)
- Ban word checking in scenes and choices
- Age-appropriate language verification

**Violation Tracking:**
- Logs all safety violations
- Categorizes by type (banned_word, inappropriate_pattern, negative_sentiment, etc.)
- Tracks severity (low, medium, high)
- Provides detailed context for review

### 2. Rate Limiting (`RateLimiter`)

Prevents abuse and ensures fair usage:

**Session Limits:**
- Max 20 turns per session per hour
- Max 100 turns per session per day

**Custom Input Limits (stricter):**
- Max 5 custom inputs per 10 minutes per session

**IP Limits:**
- Max 50 requests per IP per hour
- Max 200 requests per IP per day
- Max 10 new story starts per IP per hour

### 3. Enhanced LLM Prompts

Strengthened system prompts with explicit safety rules:

**Critical Safety Rules:**
- ABSOLUTELY NO: violence, weapons, fighting, death, blood, injuries
- ABSOLUTELY NO: scary content, monsters, ghosts, darkness, fear
- ABSOLUTELY NO: mean words, bullying, name-calling
- ABSOLUTELY NO: sad, depressing, or hopeless situations
- ONLY POSITIVE CONTENT: happy, fun, exciting, helpful, kind

### 4. Age-Appropriate Content

Different standards for different age groups:

**Ages 6-8:**
- Simple vocabulary
- Clear cause-and-effect
- Friendly characters only
- No complex or abstract concepts
- Extra restrictions on vocabulary

**Ages 9-12:**
- More complex vocabulary allowed
- Light puzzles and challenges
- Character development
- Age-appropriate problem-solving

### 5. Optional OpenAI Moderation API

Additional validation layer using OpenAI's Moderation API:

- Detects harmful content categories
- Provides backup validation
- Fail-open design (doesn't block if API is down)
- Requires API key configuration

---

## Configuration

### config.yaml

```yaml
safety:
  # Use enhanced safety filter with comprehensive checks
  use_enhanced_filter: true

  # Use OpenAI Moderation API for additional validation
  use_moderation_api: false

  # Log safety violations for review
  log_violations: true

  # Enable rate limiting to prevent abuse
  enable_rate_limiting: true

  # Maximum turns allowed per session
  max_turns_per_session: 50

  # Maximum custom inputs per 10 minutes
  max_custom_inputs_per_10min: 5
```

### Environment Variables

```bash
# Required for OpenAI Moderation API (if enabled)
OPENAI_API_KEY=sk-your-key-here
```

---

## Content Filtering

### Banned Words

The system blocks 100+ inappropriate words across categories:

- **Violence & Aggression**: kill, murder, fight, attack, weapon, gun, etc.
- **Fear & Horror**: scary, monster, ghost, zombie, nightmare, etc.
- **Negative Language**: hate, stupid, idiot, ugly, etc.
- **Danger & Risk**: poison, trap, danger, lost, abandoned, etc.
- **Excessive Sadness**: depressed, miserable, hopeless, despair, etc.

### Blocked Patterns

Regular expressions prevent:

- URLs and email addresses
- Phone numbers and addresses
- Credit card patterns
- Spam (repeated characters)
- Excessive caps (shouting)
- Social media handles and hashtags

### Sentiment Analysis

Keyword-based sentiment scoring:

- **Negative indicators**: sad, cry, afraid, lonely, angry, etc.
- **Positive indicators**: happy, fun, exciting, beautiful, kind, etc.
- **Threshold**: Content with sentiment score below -0.3 is rejected

---

## Rate Limiting

### How It Works

1. **Token Bucket Algorithm**: Tracks requests over sliding time windows
2. **Multiple Limits**: Session-based, IP-based, and custom input limits
3. **Automatic Cleanup**: Old entries are automatically removed
4. **HTTP 429 Responses**: Clear retry-after headers when limits exceeded

### Rate Limit Responses

When rate limit is exceeded:

```json
{
  "detail": "Rate limit exceeded. Please try again in 120 seconds."
}
```

HTTP Status: `429 Too Many Requests`
Header: `Retry-After: 120`

### Adjusting Limits

Edit `backend/app/services/rate_limiter.py`:

```python
self.limits = {
    "session_turns_per_hour": {
        "max_requests": 20,  # Adjust this
        "window_seconds": 3600
    },
    # ... other limits
}
```

---

## Monitoring & Admin

### Admin Endpoints

Access admin endpoints at `http://localhost:8000/api/v1/admin/`

**View Safety Violations:**
```bash
GET /api/v1/admin/safety/violations
```

Returns:
```json
{
  "total": 15,
  "by_type": {
    "banned_word": 10,
    "inappropriate_pattern": 3,
    "negative_sentiment": 2
  },
  "by_severity": {
    "high": 8,
    "medium": 5,
    "low": 2
  },
  "recent": [
    {
      "type": "banned_word",
      "severity": "high",
      "reason": "Input contains banned word: 'fight'",
      "timestamp": "2025-11-15T10:30:00"
    }
  ]
}
```

**View Rate Limiter Stats:**
```bash
GET /api/v1/admin/rate-limiter/stats
```

**Reset Rate Limiter:**
```bash
POST /api/v1/admin/rate-limiter/reset
```

⚠️ Warning: Clears all rate limit tracking. Use with caution!

**View Safety Configuration:**
```bash
GET /api/v1/admin/config/safety
```

**Detailed Health Check:**
```bash
GET /api/v1/admin/health/detailed
```

### Logging

All safety violations are logged automatically when `log_violations: true`:

```
2025-11-15 10:30:00 - app.services.safety_filter_enhanced - WARNING - Input rejected - banned word: fight
```

---

## Best Practices

### For Developers

1. **Always enable enhanced safety filter in production**
   ```yaml
   safety:
     use_enhanced_filter: true
   ```

2. **Monitor violations regularly**
   - Check `/api/v1/admin/safety/violations` weekly
   - Review patterns in flagged content
   - Adjust banned words list as needed

3. **Consider OpenAI Moderation API for additional protection**
   - Especially important for public deployments
   - Provides external validation layer
   - Costs ~$0.002 per 1K tokens

4. **Adjust rate limits based on usage**
   - Monitor `/api/v1/admin/rate-limiter/stats`
   - Increase limits for legitimate heavy users
   - Decrease limits if abuse detected

5. **Regular security updates**
   - Update banned words list periodically
   - Review and update age-inappropriate words
   - Test with edge cases regularly

### For Deployments

1. **Production Configuration**
   ```yaml
   safety:
     use_enhanced_filter: true
     use_moderation_api: true  # Recommended
     log_violations: true
     enable_rate_limiting: true
   ```

2. **Set Strong LLM Prompts**
   - Use provided enhanced prompts
   - Don't reduce safety instructions to save tokens
   - Test LLM outputs thoroughly

3. **Monitor System Health**
   - Regular checks of `/api/v1/admin/health/detailed`
   - Alert on high violation rates
   - Track rate limit hit rates

4. **Backup & Review**
   - Regularly review violation logs
   - Keep audit trail of flagged content
   - Report serious violations appropriately

### For Content Review

Weekly review checklist:

- [ ] Check `/api/v1/admin/safety/violations` for new patterns
- [ ] Review high-severity violations
- [ ] Check rate limiter stats for abuse patterns
- [ ] Test new LLM model versions for safety
- [ ] Update banned words if new issues found
- [ ] Review and archive old violation logs

---

## Fallback Responses

When LLM output is rejected, the system uses safe fallback scenes:

**Example (Space Adventure):**
```
"You float peacefully in your spaceship, looking at the beautiful twinkling stars
through the window. Your friendly robot companion beeps happily, ready to help
with your next adventure!"

Choices:
- Check the colorful control panel
- Look at the amazing star map
- Draw the beautiful stars you see
```

All fallback scenes are:
- Positive and cheerful
- Safe and welcoming
- Age-appropriate
- Engaging and fun

---

## Troubleshooting

### "Input contains inappropriate word"

**Cause**: User input contains a banned word
**Solution**: User should rephrase without the flagged word
**Admin Action**: Review if word should remain banned

### "Rate limit exceeded"

**Cause**: Too many requests in time window
**Solution**: Wait for retry-after seconds
**Admin Action**: Check if legitimate user or abuse

### "LLM output is too negative"

**Cause**: Sentiment score below threshold
**Solution**: System uses fallback response automatically
**Admin Action**: Review LLM prompts, may need strengthening

### Moderation API Errors

**Cause**: OpenAI Moderation API down or key invalid
**Solution**: System fails open (allows content)
**Admin Action**: Check API key, disable if persistent issues

---

## API Examples

### Safe Input
```bash
curl -X POST http://localhost:8000/api/v1/story/continue \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "custom_input": "I want to explore the colorful garden",
    "story_summary": "Adventure begins..."
  }'
```

✅ Accepted - Positive, appropriate content

### Blocked Input
```bash
curl -X POST http://localhost:8000/api/v1/story/continue \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "custom_input": "I want to fight the monster",
    "story_summary": "Adventure begins..."
  }'
```

❌ Rejected - Contains banned words "fight" and "monster"

---

## Version History

- **v0.6.0** (Phase 6): Enhanced safety features
  - Comprehensive banned words list (100+ terms)
  - Sentiment analysis
  - Age-appropriate content filtering
  - Rate limiting
  - Optional OpenAI Moderation API
  - Admin monitoring endpoints
  - Violation logging and tracking

- **v0.3.0** (Phase 3): Basic safety filter
  - Basic banned words (25 terms)
  - Simple pattern matching
  - Basic sentiment check

---

## Support

For questions or to report safety concerns:

- Review `/api/v1/admin/` endpoints
- Check server logs for details
- Consult `backend/README.md` for configuration help
- See `StoryQuest_Plan.md` for architecture details

**Remember**: Child safety is paramount. When in doubt, be more restrictive rather than permissive.
