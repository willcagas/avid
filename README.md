# AI Voice Dictation

A lightweight, personal dictation tool for macOS that uses:

- **Local ASR**: `whisper.cpp` (fast, private for audio)
- **AI formatting**: Cloud LLM to rewrite into **Email mode** or **Message mode**
- **Push-to-talk**: Hold a key to record, release to transcribe + rewrite + paste

## Features

- Push-to-talk dictation with configurable hotkey
- Two output modes: Email (professional) and Message (casual)
- Local speech-to-text via whisper.cpp (audio stays private)
- Cloud LLM formatting (only text sent, not audio)
- Auto-paste into focused application (optional)
- Low CPU overhead when idle

## Requirements

- macOS (Apple Silicon: M4 Pro/Max)
- Python 3.11+
- whisper.cpp (via Homebrew)
- OpenAI API key (for LLM formatting)

## Quick Start

### Install Dependencies

```bash
brew install whisper-cpp
python3 -m venv .venv
source .venv/bin/activate
pip install sounddevice numpy pynput python-dotenv requests scipy
```

### Download Whisper Model

```bash
mkdir -p ~/models/whisper
cd ~/models/whisper
curl -L -o ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

### Configure

```bash
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY and adjust settings
```

### Run

```bash
python -m src.main
```

## Configuration

See `.env.example` for all available configuration options:

- `OPENAI_API_KEY` - Your OpenAI API key
- `LLM_MODEL` - Model to use for formatting (default: gpt-4o-mini)
- `MODE` - Default mode: email or message
- `AUTO_PASTE` - Auto-paste into focused app (requires Accessibility permission)
- `WHISPER_BIN` - Path to whisper-cpp binary
- `WHISPER_MODEL_PATH` - Path to whisper model file
- `PTT_KEY` - Push-to-talk key (default: alt_r)

## Permissions

- **Microphone**: Required for recording
- **Accessibility**: Required only if `AUTO_PASTE=true` (to simulate ⌘V)

## License

MIT
