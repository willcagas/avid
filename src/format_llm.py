# format_llm.py
"""
Formatter component for rewriting transcripts using cloud LLM.

Uses OpenAI API with strict constraints to format dictated text
into professional emails or casual messages.
"""

from typing import Literal

import requests

from .config import Config
from .prompts import get_system_prompt, get_user_prompt
from .utils import setup_logging

logger = setup_logging()


class Formatter:
    """Formats transcripts using OpenAI API."""

    def __init__(self, config: Config):
        """
        Initialize the formatter.
        
        Args:
            config: Application configuration with API settings
        """
        self.api_key = config.openai_api_key
        self.api_url = config.openai_api_url
        self.model = config.llm_model
        self.timeout = config.llm_timeout
        self.temperature = config.llm_temperature
        self._enabled = bool(self.api_key)

        if not self._enabled:
            logger.warning("Formatter disabled - no API key configured")

    def format(
        self,
        raw_text: str,
        mode: Literal["email", "message", "prompt"]
    ) -> str:
        """
        Format raw transcript using the LLM.
        
        Args:
            raw_text: Raw speech-to-text transcript
            mode: Formatting mode ("email", "message", or "prompt")
        
        Returns:
            Formatted text, or raw_text on failure
        """
        if not raw_text.strip():
            return raw_text

        if not self._enabled:
            logger.info("Formatter disabled, returning raw text")
            return raw_text

        # Estimate max tokens (roughly 1.5x input for some expansion room)
        estimated_tokens = len(raw_text.split()) * 2
        max_tokens = max(100, min(estimated_tokens, 1000))

        # Build request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": get_system_prompt(mode)},
                {"role": "user", "content": get_user_prompt(mode, raw_text)}
            ],
            "temperature": self.temperature,
            "max_tokens": max_tokens
        }

        logger.info(f"Formatting ({mode} mode): {len(raw_text)} chars")

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            formatted = data["choices"][0]["message"]["content"].strip()

            usage = data.get("usage", {})
            prompt_tok = usage.get("prompt_tokens", 0)
            comp_tok = usage.get("completion_tokens", 0)
            logger.info(f"OpenAI Usage: {prompt_tok} prompt + {comp_tok} completion tokens")

            logger.info(f"Formatted: {len(formatted)} chars")
            return formatted

        except requests.Timeout:
            logger.error("Formatter timeout - returning raw text")
            return raw_text
        except requests.RequestException as e:
            logger.error(f"Formatter API error: {e} - returning raw text")
            return raw_text
        except (KeyError, IndexError) as e:
            logger.error(f"Formatter response parsing error: {e}")
            return raw_text
        except Exception as e:
            logger.error(f"Formatter unexpected error: {e}")
            return raw_text

    @property
    def enabled(self) -> bool:
        """Check if formatter is enabled."""
        return self._enabled
