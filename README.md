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

### Run with UI Overlay

For visual feedback with waveform and sound cues:

```bash
python -m src.main --ui
```

This shows a floating overlay that displays:
- 🎤 Waveform visualization while recording
- ⏳ Processing spinner during transcription
- ✓ Success indicator when done
- Sound feedback on start/stop

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

### Microphone Access
Required for recording. macOS will prompt automatically on first use.

### Accessibility (for Auto-paste)

To enable auto-paste (`AUTO_PASTE=true`), grant Accessibility access:

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button
3. Add **Terminal** (or your IDE, e.g., VS Code, iTerm)
4. Toggle it **ON**

> **Note**: If the app still shows "not trusted" warnings, try removing and re-adding it from the list.

### Enable Auto-paste

1. Edit your `.env` file:
   ```
   AUTO_PASTE=true
   ```
2. Restart the app
3. Text will now paste directly into the focused application

## Launch at Login

To have AI Voice Dictation start automatically when you log in:

### Install

```bash
./scripts/install_launchagent.sh
```

This will:
- Copy the LaunchAgent plist to `~/Library/LaunchAgents/`
- Load the agent immediately
- Configure it to start on every login

### Start/Stop Manually

```bash
# Start
launchctl start com.user.aidictation

# Stop
launchctl stop com.user.aidictation
```

### Uninstall

```bash
./scripts/uninstall_launchagent.sh
```

### Logs

If something isn't working, check the logs:

```bash
tail -f /tmp/aidictation.out.log
tail -f /tmp/aidictation.err.log
```

## License

MIT
