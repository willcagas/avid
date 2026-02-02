# config.py
"""
Configuration management for the AI Voice Dictation application.

Loads settings from environment variables (.env file) with sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

from .utils import expand_path, setup_logging

logger = setup_logging()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI
    openai_api_key: str
    openai_api_url: str
    llm_model: str
    llm_timeout: int
    llm_temperature: float

    # Dictation mode
    mode: Literal["default", "message", "email", "notes", "prompt"]

    # Auto-paste setting
    auto_paste: bool

    # Whisper.cpp
    whisper_bin: str
    whisper_server_bin: str
    whisper_port: int
    whisper_model_path: str
    whisper_timeout: int

    # Push-to-talk key
    ptt_key: str

    def __init__(self):
        """Load configuration from environment variables."""
        # Load .env file from project root
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        # Required settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - LLM formatting will be disabled")

        # LLM settings
        self.openai_api_url = os.getenv(
            "OPENAI_API_URL",
            "https://api.openai.com/v1/chat/completions"
        )
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.llm_timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

        # Dictation mode (managed dynamically via UI, starts at default)
        self.mode: Literal["default", "message", "email", "notes", "prompt"] = "default"

        # Auto-paste
        self.auto_paste = os.getenv("AUTO_PASTE", "false").lower() == "true"

        # Whisper settings
        self.whisper_bin = os.getenv("WHISPER_BIN", "whisper-cli")
        self.whisper_server_bin = os.getenv("WHISPER_SERVER_BIN", "whisper-server")
        self.whisper_port = int(os.getenv("WHISPER_PORT", "8080"))
        whisper_model = os.getenv("WHISPER_MODEL_PATH", "~/models/whisper/ggml-medium.en-q5_0.bin")
        self.whisper_model_path = expand_path(whisper_model)
        self.whisper_timeout = int(os.getenv("WHISPER_TIMEOUT", "60"))

        # Validate whisper model exists
        if not Path(self.whisper_model_path).exists():
            logger.warning(f"Whisper model not found at: {self.whisper_model_path}")

        # PTT key
        self.ptt_key = os.getenv("PTT_KEY", "alt_r")

    def __repr__(self) -> str:
        return (
            f"Config(mode={self.mode}, auto_paste={self.auto_paste}, "
            f"ptt_key={self.ptt_key}, model={self.llm_model})"
        )
