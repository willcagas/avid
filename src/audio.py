# audio.py
"""
AudioRecorder component for capturing microphone input.

Uses sounddevice + NumPy for audio capture at 16kHz mono.
Saves output as WAV file for whisper.cpp processing.
"""

import threading

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from .utils import setup_logging

logger = setup_logging()

# Audio settings for whisper.cpp compatibility
SAMPLE_RATE = 16000  # 16kHz
CHANNELS = 1  # Mono
DTYPE = np.float32  # Float32 for sounddevice


class AudioRecorder:
    """Records audio from microphone and saves to WAV file."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS):
        """
        Initialize the audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels

        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._is_recording = False
        self._lock = threading.Lock()

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags
    ) -> None:
        """Callback for audio stream - buffers incoming frames."""
        if status:
            logger.warning(f"Audio callback status: {status}")

        if self._is_recording:
            self._frames.append(indata.copy())

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        with self._lock:
            if self._is_recording:
                logger.warning("Already recording")
                return

            self._frames = []
            self._is_recording = True

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=DTYPE,
                callback=self._audio_callback
            )
            self._stream.start()
            logger.info("Recording started")

    def stop_recording(self, output_path: str) -> bool:
        """
        Stop recording and save audio to WAV file.
        
        Args:
            output_path: Path to save the WAV file
        
        Returns:
            True if audio was saved successfully, False otherwise
        """
        with self._lock:
            if not self._is_recording:
                logger.warning("Not currently recording")
                return False

            self._is_recording = False

            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            if not self._frames:
                logger.warning("No audio frames captured")
                return False

            # Concatenate all frames
            audio_data = np.concatenate(self._frames, axis=0)

            # Convert float32 to int16 for WAV file
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Save as WAV
            try:
                wavfile.write(output_path, self.sample_rate, audio_int16)
                duration = len(audio_data) / self.sample_rate
                logger.info(f"Recording saved: {output_path} ({duration:.1f}s)")
                return True
            except Exception as e:
                logger.error(f"Failed to save audio: {e}")
                return False

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def get_amplitude(self) -> float:
        """
        Get the current audio amplitude (0.0 to 1.0).
        
        Uses the most recent audio frame to calculate RMS amplitude.
        Returns 0.0 if not recording or no frames available.
        """
        if not self._is_recording or not self._frames:
            return 0.0

        try:
            # Use the most recent frame
            recent_frame = self._frames[-1]
            # Calculate RMS (root mean square) amplitude
            rms = np.sqrt(np.mean(recent_frame ** 2))
            # Normalize to 0-1 range (typical speech is around 0.01-0.1 RMS)
            amplitude = min(1.0, rms * 10)
            return float(amplitude)
        except Exception:
            return 0.0
