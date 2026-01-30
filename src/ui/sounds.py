# sounds.py
"""Audio feedback for recording start/stop."""

import subprocess
import os
from pathlib import Path

# Get the sounds directory path
SOUNDS_DIR = Path(__file__).parent / "web" / "sounds"


def play_sound(filename: str) -> None:
    """
    Play a sound file using macOS afplay.
    
    Non-blocking: sound plays in background.
    
    Args:
        filename: Name of the sound file in the sounds directory
    """
    sound_path = SOUNDS_DIR / filename
    if sound_path.exists():
        # Use afplay (macOS built-in) - non-blocking with &
        subprocess.Popen(
            ["afplay", str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def play_start_sound() -> None:
    """Play the recording start sound."""
    play_sound("start.wav")


def play_stop_sound() -> None:
    """Play the recording stop sound."""
    play_sound("stop.wav")
