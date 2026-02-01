# ui/__init__.py
"""UI overlay module for AI Voice Dictation."""

from .sounds import play_start_sound, play_stop_sound
from .window import DictationWindow

__all__ = ["DictationWindow", "play_start_sound", "play_stop_sound"]
