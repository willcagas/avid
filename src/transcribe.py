# transcribe.py
"""
Transcriber component for converting audio to text using whisper.cpp.

Invokes whisper-cpp CLI with the audio file and parses the output.
"""

import os
import subprocess
from pathlib import Path

import requests

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
        self.config = config
        self.whisper_bin = config.whisper_bin
        self.model_path = config.whisper_model_path
        self.timeout = config.whisper_timeout

        # Get number of CPU cores for threading (use half)
        self.threads = max(1, os.cpu_count() // 2) if os.cpu_count() else 4

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file using the local whisper server.
        
        Args:
            audio_path: Path to the WAV file
        
        Returns:
            Transcript text, or empty string on failure
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return ""

        url = f"http://127.0.0.1:{self.config.whisper_port}/inference"
        
        logger.info(f"Transcribing via server: {audio_path}")
        
        try:
            with open(audio_file, 'rb') as f:
                files = {'file': f}
                # response_format='text' creates simpler output, or json for more details
                # whisper.cpp server usually takes multipart/form-data
                response = requests.post(
                    url, 
                    files=files, 
                    data={'response_format': 'text'},
                    timeout=self.timeout
                )
            
            if response.status_code == 200:
                transcript = response.text.strip()
                # If json is returned despite requesting text, parse it
                # But standard whisper-server output depends on implementation. 
                # Let's assume text for now based on typical usage, 
                # or we can parse JSON if it returns that.
                # Actually, whisper.cpp server default might be JSON. 
                # Let's try to parse JSON if it looks like it.
                
                try:
                    data = response.json()
                    if 'text' in data:
                        transcript = data['text'].strip()
                except Exception:
                    pass # It was probably plain text
                
                logger.info(f"Transcription complete: {len(transcript)} chars")
                return transcript
            else:
                logger.error(f"Server error {response.status_code}: {response.text}")
                return ""

        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Whisper server. Is it running?")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
