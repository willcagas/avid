# config.py
"""
Configuration management for the AI Voice Dictation application.

Loads settings from environment variables (.env file) with sensible defaults.

Environment Variables:
- OPENAI_API_KEY: API key for OpenAI
- LLM_MODEL: Model name (default: gpt-4o-mini)
- MODE: Dictation mode - "email" or "message" (default: email)
- AUTO_PASTE: Whether to auto-paste (default: false)
- WHISPER_BIN: Path to whisper-cpp binary (default: whisper-cpp)
- WHISPER_MODEL_PATH: Path to whisper model file
- PTT_KEY: Push-to-talk key (default: alt_r)
"""

# TODO: Load environment variables using python-dotenv
# TODO: Define Config dataclass or class with all settings
# TODO: Validate required settings (e.g., API key, model path)
# TODO: Expand ~ in paths
