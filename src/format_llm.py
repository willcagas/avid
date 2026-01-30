# format_llm.py
"""
Formatter component for rewriting transcripts using cloud LLM.

Responsibilities:
- Take raw transcript + mode (email/message)
- Call cloud LLM API with appropriate prompts
- Return formatted text
- On failure, return raw transcript (never block user)

LLM Settings:
- Model: gpt-4o-mini (configurable)
- Temperature: 0.2-0.4 (stable output)
- Max tokens: capped to input length

Safety:
- Never add new facts
- Preserve names, dates, numbers, URLs exactly
"""

# TODO: Implement Formatter class
# TODO: Use requests or openai library for API calls
# TODO: Build system prompt + user message from prompts.py
# TODO: Set temperature and max_tokens appropriately
# TODO: Implement fallback to raw transcript on any failure
# TODO: Add timeout handling
