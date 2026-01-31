# TDD — AViD: AI Voice Dictation (macOS, Push-to-Talk, Whisper.cpp + Cloud Rewriter)

**Goal:** A lightweight, personal dictation tool on macOS that uses:

* **Local ASR**: `whisper.cpp` (fast, private for audio)
* **AI formatting**: a **cloud LLM** to rewrite into **Message**, **Email**, **Notes**, or **Prompt** mode
* **Push-to-talk**: hold a key to record, release to transcribe + rewrite + paste
* **Visual overlay**: Floating UI with waveform visualization and mode controls

---

## 1) Requirements

### Functional

* Push-to-talk (hold key):

  * On keydown: start recording
  * On keyup: stop recording and process
* Four output modes:

  * **Message**: casual, short, conversational
  * **Email**: professional, complete sentences, nice punctuation/paragraphs
  * **Notes**: semi-structured, scannable, fragment-tolerant (no invention of content)
  * **Prompt**: AI prompt engineering using CO-STAR framework (Context, Objective, Style, Tone, Audience, Response)
* Output behavior:

  * Always copy to clipboard
  * Optional: auto-paste into the focused app
* Runs as a lightweight background app:

  * LaunchAgent service that starts at login
  * Floating UI overlay with waveform visualization
  * Draggable window that maintains position between states
  * Smart click detection (distinguishes taps from drags)
* Safe rewriting:

  * Don’t add new facts
  * Preserve names/dates/numbers/URLs

### Non-functional

* Low CPU overhead idle
* Low latency end-to-end for short dictations
* Audio stays local; only text goes to cloud
* Resilient: if formatter fails, paste raw transcript

---

## 2) Tech Choices

### OS / Platform

* macOS (Apple Silicon: M4 Pro/Max)

### Language / Runtime

* Python 3.11+ (venv)

### Audio capture

* `sounddevice` + NumPy (records float32 PCM at 16kHz mono)

### Push-to-talk hotkey

* `pynput` global key listener (keydown/keyup)

  * Recommended PTT key: `Right Option (alt_r)` or `F18`

### ASR (local)

* `whisper.cpp` installed via Homebrew (`brew install whisper-cpp`) or bundled later
* Model: `ggml-base.en.bin` (fast, solid), upgrade to `small.en` if desired

### Formatter (cloud LLM)

* OpenAI “mini” tier model (fast + cheap for rewriting)
* Call: Responses API (or Chat Completions if you prefer); the design below is API-agnostic.

### Pasting

* Always: `pbcopy` (clipboard)
* Optional paste: `osascript` to press ⌘V (requires Accessibility permission)

### UI Overlay

* **Implemented**: pywebview-based floating overlay
* **Features**:
  * Waveform visualization during recording
  * Processing spinner with mode badge
  * Settings menu for mode switching
  * Draggable, maintains position across resize
  * Smart click detection (tap vs drag/long-press)
  * Dynamic window resizing (60x60 idle, 260x80 expanded)
  * Instant feedback (no lingering "Copied!" message)

---

## 3) System Architecture

### Components

1. **HotkeyListener**

   * Detects PTT key down/up
   * Emits `START_RECORDING` / `STOP_RECORDING`

2. **AudioRecorder**

   * Starts InputStream at 16kHz mono
   * Buffers frames only while recording
   * Outputs `audio.wav` (16kHz mono)

3. **Transcriber (Whisper)**

   * Invokes `whisper-cpp` CLI with model path and wav path
   * Parses transcript output (text)

4. **Formatter (LLM)**

   * Uses `mode` + `raw_transcript`
   * Calls cloud LLM with strict constraints
   * Returns `formatted_text`
   * On failure: returns `raw_transcript`

5. **Injector**

   * Copies `formatted_text` to clipboard
   * Optionally triggers ⌘V paste

6. **ModeManager**

   * Stores current mode (`message` / `email` / `notes` / `prompt`)
   * Cycle order: message → email → notes → prompt
   * Optional per-app default later

---

## 4) Data Flow

**PTT key down**
→ AudioRecorder starts buffering frames

**PTT key up**
→ AudioRecorder writes `/tmp/utt.wav` (16kHz mono)
→ Transcriber returns `raw_text`
→ Formatter returns `final_text` (or raw if failure)
→ Injector copies + pastes into focused app

---

## 5) File/Repo Layout (you can use this)

```
ai-dictation/
  README.md
  pyproject.toml  (or requirements.txt)
  .env.example
  src/
    main.py
    config.py
    hotkeys.py
    audio.py
    transcribe.py
    format_llm.py
    inject.py
    prompts.py
    utils.py
  models/               (optional; or store in ~/models/whisper)
  scripts/
    run.sh
    install_launchagent.sh
  launchd/
    com.yourname.aidictation.plist
```

---

## 6) Configuration

### Environment variables

`.env`

* `OPENAI_API_KEY=...`
* `LLM_MODEL=gpt-4o-mini` (or equivalent mini model you choose)
* `MODE=message` (default; options: message, email, notes, prompt)
* `AUTO_PASTE=false`
* `WHISPER_BIN=whisper-cpp`
* `WHISPER_MODEL_PATH=~/models/whisper/ggml-base.en.bin`
* `PTT_KEY=alt_r` (or `f18`)

### Defaults

* Start in `message` mode (most common use case for quick replies)
* Mode cycle: message → email → notes → prompt
* Auto-paste off until permissions are set.

---

## 7) Whisper.cpp Invocation

### Audio requirements

Always feed **16kHz mono WAV**.

### Suggested CLI

Example:

* threads: half your CPU cores (fast without overloading)
* output to txt (easy parsing)

Implementation detail:

* Use `subprocess.run([...], check=True)` and read produced `.txt` file.

---

## 8) LLM Formatter Design

### Prompting strategy

Use **one system prompt** + **one user message**:

* System: strict transformer
* User: mode instruction + transcript

#### System prompt (shared)

* “You are a dictation formatter.”
* “Rewrite without adding new information.”
* “Preserve names, dates, numbers, URLs exactly.”
* “If unclear, keep original wording.”
* “Return only rewritten text (no markdown, no quotes).”

#### Mode prompts

* **Email mode**: professional, full sentences, clean paragraphing, concise; optional greeting/signoff only if user said it
* **Message mode**: casual, short, conversational; minimal punctuation ok; no greeting/signoff
* **Notes mode**: semi-structured, scannable notes
  * Favors clarity over polish
  * Accepts fragments and incomplete sentences
  * Uses bullets only when speaker clearly listed items
  * Uses headings only when speaker indicated sections
  * Removes filler words but preserves original wording
  * Conservative: never invents structure or content
* **Prompt mode**: AI Prompt Engineer using CO-STAR framework
  * **C**ontext: Background information
  * **O**bjective: What the AI should accomplish
  * **S**tyle: Writing style to use
  * **T**one: Emotional tone
  * **A**udience: Target audience
  * **R**esponse: Expected response format

### Safety/factuality

* Never “invent details”; you’ll enforce this via the prompt and by limiting temperature.

### Model settings

* `temperature`: 0.2–0.4 (keeps it stable)
* `max_output_tokens`: cap to roughly input length (prevents rambling)

### Failure handling

* If API times out / fails:

  * Return `raw_text`
  * Still copy/paste raw so the tool never blocks you

### Cost expectation

At ~2000 words/week, formatter cost is effectively **pennies/month** on “mini” models (you won’t notice it).

---

## 9) Privacy & Permissions

### Privacy

* Audio stays local
* Only transcript text sent to cloud
* Do not log transcripts by default

### macOS permissions

* **Microphone**: required for recording
* **Accessibility**: required only if `AUTO_PASTE=true` (to simulate ⌘V)

  * Clipboard-only mode avoids this

---

## 10) Performance Considerations

### Latency

* Biggest wins:

  * Use `base.en` or `small.en` model
  * Keep audio 16k mono
  * Use `whisper.cpp` Metal build (brew should be optimized)
  * Keep formatter output short (cap tokens)

### CPU usage

* Idle should be near zero:

  * listener thread + no audio processing
* Only spikes when you release PTT (transcribe + format)

---

## 11) Rollout Plan (so you can actually use it)

### Phase 1 — CLI MVP (1 evening)

* Implement components without UI
* Run from Terminal
* Clipboard-only output
* Verify reliability

### Phase 2 — Auto-paste + permissions (30 min)

* Enable Accessibility for Terminal or packaged app
* Turn on `AUTO_PASTE=true`

### Phase 3 — Menubar + mode toggle (optional)

* Add `rumps` menu: Mode: Email/Message, Auto-paste on/off, Quit
* Still lightweight

### Phase 4 — Launch at login

* Add LaunchAgent `.plist` that starts your tool on boot

### Phase 5 — UI Overlay + Audio Feedback ✅ COMPLETED

**Implemented Features:**

#### Visual Overlay (pywebview)
* **Idle state**: 60x60px floating icon (draggable)
* **Recording state**: 260x80px with live waveform visualization
* **Processing state**: Spinner with mode badge
* **Settings menu**: Mode toggle (Email/Message/Prompt), accessible via tap

#### Smart Interactions
* **Tap detection**: < 300ms click opens menu
* **Long press/drag**: > 300ms or movement > 5px = window drag (no menu)
* **Dynamic resizing**: Window expands/contracts around current center point
* **Position memory**: Maintains user-dragged position across state changes

#### Visual Design
* **Color themes**:
  * Message mode: Green (#38ef7d)
  * Email mode: Purple (#667eea)
  * Notes mode: Cyan/Teal (#00BCD4)
  * Prompt mode: Orange (#FF9F43)
* **Animations**: Flash feedback on mode switch, smooth state transitions
* **No shadows**: Flat design for minimal visual footprint

#### Audio Feedback
* Start recording: Subtle beep
* Stop recording: Confirmation tone
* Bundled WAV files in `src/ui/sounds/`

#### Implementation Details
* **Technology**: pywebview (Python-first, native webview)
* **UI Stack**: HTML/CSS/JS with Canvas API for waveform
* **Communication**: Python ↔ JS bridge via `window.pywebview.api`
* **Window Management**: Dynamic resize with center-point preservation
* **State Management**: `set_ui_state('idle'|'expanded')` triggers resize

#### Usage Logging
* Real-time OpenAI token usage logging in terminal
* Format: `[INFO] OpenAI Usage: {prompt} prompt + {completion} completion tokens`
* Helps track API consumption without waiting for dashboard updates

---

## 12) Testing Plan

### Manual test cases

* PTT press/release produces transcript
* Email mode produces professional output
* Message mode produces casual output
* If LLM is unavailable → raw transcript still copied/pasted
* Very short utterance (1–2 words) works
* Long utterance (2–3 min) works (may be slower)

### Regression checks

* Verify WAV is 16kHz mono
* Verify no stuck “recording” state if key events are missed

---

## 13) “Definition of Done”

You can run it daily when:

* Hold PTT → speak → release → text appears in Slack/Mail reliably
* Switching mode changes tone correctly
* If cloud formatter fails, you still get usable text
* CPU stays low when idle

---

## 14) README Quick Start (copy/paste)

### Install

```bash
brew install whisper-cpp
python3 -m venv .venv
source .venv/bin/activate
pip install sounddevice numpy pynput python-dotenv requests scipy pywebview
```

### Model

```bash
mkdir -p ~/models/whisper
cd ~/models/whisper
curl -L -o ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

### Run

```bash
cp .env.example .env
# edit .env to add OPENAI_API_KEY and model path
python -m src.main
```