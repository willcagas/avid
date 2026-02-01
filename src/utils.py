# utils.py
"""
Utility functions for the AI Voice Dictation application.

Common utilities used across modules:
- Logging setup
- Path expansion (~ to home directory)
- Temporary file management
"""

import logging
import os
from pathlib import Path

# Default temp audio path
TEMP_AUDIO_PATH = "/tmp/utt.wav"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the application logger.
    
    Args:
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("ai-dictation")

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


def expand_path(path: str) -> str:
    """
    Expand ~ to home directory and resolve the path.
    
    Args:
        path: Path string that may contain ~
    
    Returns:
        Expanded absolute path string
    """
    return str(Path(os.path.expanduser(path)).resolve())


def get_temp_audio_path() -> str:
    """
    Return the temporary audio file path.
    
    Returns:
        Path to temporary WAV file (/tmp/utt.wav)
    """
    return TEMP_AUDIO_PATH



