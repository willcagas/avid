# transcribe.py
"""
Transcriber component for converting audio to text using whisper.cpp.

Invokes whisper-cpp CLI with the audio file and parses the output.
"""

import os
import subprocess
from pathlib import Path

from .config import Config
from .utils import setup_logging

logger = setup_logging()


class Transcriber:
    """Transcribes audio files using whisper.cpp CLI."""

    def __init__(self, config: Config):
        """
        Initialize the transcriber.
        
        Args:
            config: Application configuration with whisper settings
        """
        self.whisper_bin = config.whisper_bin
        self.model_path = config.whisper_model_path
        self.timeout = config.whisper_timeout

        # Get number of CPU cores for threading (use half)
        self.threads = max(1, os.cpu_count() // 2) if os.cpu_count() else 4

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the WAV file (must be 16kHz mono)
        
        Returns:
            Transcript text, or empty string on failure
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return ""

        # Output file path (whisper-cpp adds .txt extension)
        output_base = str(audio_file.with_suffix(""))
        output_txt = output_base + ".txt"

        # Build whisper-cpp command
        cmd = [
            self.whisper_bin,
            "-m", self.model_path,
            "-f", audio_path,
            "-t", str(self.threads),
            "-otxt",  # Output to txt file
            "-of", output_base,  # Output file base name
            "--no-timestamps",  # Don't include timestamps
        ]

        logger.info(f"Transcribing: {audio_path}")

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.timeout
            )

            # Read the output text file
            if Path(output_txt).exists():
                transcript = Path(output_txt).read_text().strip()
                # Clean up the output file
                Path(output_txt).unlink()
                logger.info(f"Transcription complete: {len(transcript)} chars")
                return transcript
            else:
                logger.error("Whisper did not produce output file")
                return ""

        except subprocess.CalledProcessError as e:
            logger.error(f"Whisper failed: {e.stderr}")
            return ""
        except subprocess.TimeoutExpired:
            logger.error("Whisper timed out")
            return ""
        except FileNotFoundError:
            logger.error(f"Whisper binary not found: {self.whisper_bin}")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
