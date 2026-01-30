# prompts.py
"""
LLM prompt templates for dictation formatting.

Contains system prompts and mode-specific instructions for the formatter.

Prompt Strategy:
- One system prompt (shared) defining the formatter role and constraints
- Mode-specific user prompts for email vs message formatting

System Prompt Constraints:
- Rewrite without adding new information
- Preserve names, dates, numbers, URLs exactly
- If unclear, keep original wording
- Return only rewritten text (no markdown, no quotes)

Modes:
- Email: professional, full sentences, clean paragraphing
- Message: casual, short, conversational
"""

# TODO: Define SYSTEM_PROMPT constant
# TODO: Define EMAIL_MODE_PROMPT template
# TODO: Define MESSAGE_MODE_PROMPT template
# TODO: Implement get_prompt(mode, transcript) function
