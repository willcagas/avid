# audio.py
"""
AudioRecorder component for capturing microphone input.

Responsibilities:
- Start/stop audio recording on demand
- Capture audio at 16kHz mono (required by whisper.cpp)
- Buffer frames while recording
- Save output as WAV file to /tmp/utt.wav

Uses sounddevice + NumPy for audio capture.
"""

# TODO: Implement AudioRecorder class
# TODO: Use sounddevice.InputStream at 16kHz mono
# TODO: Buffer frames in memory while recording
# TODO: Use scipy.io.wavfile to write WAV output
# TODO: Ensure thread-safe start/stop operations
