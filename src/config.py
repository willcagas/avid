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
    llm_model: str
    
    # Dictation mode
    mode: Literal["email", "message", "prompt", "notes"]
    
    # Auto-paste setting
    auto_paste: bool
    
    # Whisper.cpp
    whisper_bin: str
    whisper_model_path: str
    
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
        
        # LLM model
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        # Dictation mode
        mode_val = os.getenv("MODE", "message").lower()
        if mode_val not in ("email", "message", "prompt", "notes"):
            logger.warning(f"Invalid MODE '{mode_val}', defaulting to 'message'")
            mode_val = "message"
        self.mode = mode_val  # type: ignore
        
        # Auto-paste
        self.auto_paste = os.getenv("AUTO_PASTE", "false").lower() == "true"
        
        # Whisper settings
        self.whisper_bin = os.getenv("WHISPER_BIN", "whisper-cli")
        whisper_model = os.getenv("WHISPER_MODEL_PATH", "~/models/whisper/ggml-base.en.bin")
        self.whisper_model_path = expand_path(whisper_model)
        
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
