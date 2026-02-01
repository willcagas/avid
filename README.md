
<div align="center">
  <img src="assets/avid_logo.png" width="128" height="128" alt="AViD Logo">
  <h1>AViD</h1>
  <h3>AI VoIce Dictation</h3>
  <p>Experimental internal tool for high-speed, AI-formatted voice input on macOS.</p>
</div>

---

> **internal-tool**: This project is built primarily for the creator's personal workflow. <br>
> You are free to fork and use it, but you must bring your own **OpenAI API Key** for the AI formatting features.

## Overview

**AViD** allows you to dictate text using Push-to-Talk, transcribing it locally with `whisper.cpp` for speed and privacy, then instantly rewriting it via GPT-4o into polished text before auto-pasting it into your active window.

- **Local Transcription**: Uses `whisper.cpp` (Metal accelerated) for fast, private ASR.
- **AI Formatting**: Cloud LLM rewrites your raw speech into structured text.
- **Push-to-Talk**: Hold `Right Option` (configurable) to record. Release to process.
- **5 Output Modes** (toggle via UI):
  - **Default**: Standard cleanup (starting mode)
  - **Message**: Casual, all lowercase, no trailing punctuation
  - **Email**: Professional, complete sentences
  - **Notes**: Semi-structured, scannable notes
  - **Prompt**: AI prompt engineering using CO-STAR framework
- **Auto-Paste**: Directly injects the formatted text into your focused application.

## Prerequisites

- **macOS** (Optimized for Apple Silicon)
- **Python 3.11+**
- **Homebrew**
- **OpenAI API Key** (Required for LLM formatting)

## Setup Guide

### 1. Install System Dependencies

```bash
brew install whisper-cpp
```

### 2. Download Whisper Model

Download a model for local transcription (Base English recommended for speed/accuracy balance):

```bash
mkdir -p ~/models/whisper
cd ~/models/whisper
curl -L -o ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

### 3. Clone & Python Setup

```bash
# Clone the repository
git clone https://github.com/willcagas/avid.git
cd avid

# Setup Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python Requirements
pip install sounddevice numpy pynput python-dotenv requests scipy pywebview
```

### 4. Configuration

Create your `.env` file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API Key:
```
OPENAI_API_KEY=sk-your-key-here
PTT_KEY=alt_r
AUTO_PASTE=true
```

## Permissions

AViD needs system permissions to function correctly:
1.  **Microphone**: For recording audio.
2.  **Accessibility**: For simulating keystrokes (Auto-Paste). Go to **System Settings > Privacy & Security > Accessibility** and add your **Terminal** or IDE (e.g., VSCode, iTerm).

### Running the App

To start AViD:

1.  Double-click **`AViD.command`** in the project folder.
2.  The Terminal window will appear for a split second and then vanish (this is normal).
3.  The **AViD** overlay (microphone icon) will appear at the bottom of your screen.

- **Hold** `Right Option` to record.
- **Speak** your thought.
- **Release** to process.
- The overlay will show the status; text will auto-paste when ready.

> **Note**: The first time you run it, macOS may ask for **Microphone** and **Accessibility** permissions. Grant them to allow recording and auto-pasting.

### Auto-Start at Login

To have AViD run automatically when you log in:

1.  Open **System Settings**.
2.  Go to **General > Login Items**.
3.  Click the **+** button under "Open at Login".
4.  Navigate to the `avid` folder and select the `AViD.command` file.

## Project Structure

- `AViD.command`: Double-clickable launcher app (hides terminal).
- `src/main.py`: Application entry point.
- `src/audio.py`: Audio recording via `sounddevice`.
- `src/transcribe.py`: Local transcription handling.
- `src/format_llm.py`: Logic for GPT-4o formatting.
- `src/ui/`: WebView based UI overlay (HTML/CSS/JS).

## License

MIT
