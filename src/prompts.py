# prompts.py
"""
LLM prompt templates for dictation formatting.

Contains system prompts and mode-specific instructions for the formatter.
The prompts are designed to format text WITHOUT changing words.
"""

from typing import Literal

# System prompt - strict constraints to preserve original words
SYSTEM_PROMPT = """You are a dictation formatter. Your ONLY job is to add punctuation and fix capitalization.

CRITICAL RULES - NEVER BREAK THESE:
1. NEVER change, replace, or substitute any words
2. NEVER add words that weren't spoken
3. NEVER remove words that were spoken
4. NEVER paraphrase or "improve" the wording
5. Keep every single word from the original, in the same order

You may ONLY:
- Add punctuation (periods, commas, question marks, etc.)
- Fix capitalization
- Remove filler words like "um", "uh", "like" (only clear filler)
- Fix obvious spelling of proper nouns

Return ONLY the formatted text. No quotes, no markdown, no explanations."""

# Mode-specific prompts
EMAIL_MODE_PROMPT = """Format this transcript for an email.
Add proper punctuation and capitalization. Use complete sentences.
DO NOT change any words - only add punctuation and fix caps.

Transcript: {transcript}"""

MESSAGE_MODE_PROMPT = """Format this transcript for a casual message.
Add minimal punctuation. Keep it natural.
DO NOT change any words - only add punctuation if needed.

Transcript: {transcript}"""


def get_user_prompt(mode: Literal["email", "message"], transcript: str) -> str:
    """
    Build the user prompt for the given mode and transcript.
    
    Args:
        mode: Either "email" or "message"
        transcript: Raw speech-to-text transcript
    
    Returns:
        Formatted user prompt string
    """
    if mode == "email":
        return EMAIL_MODE_PROMPT.format(transcript=transcript)
    else:
        return MESSAGE_MODE_PROMPT.format(transcript=transcript)
