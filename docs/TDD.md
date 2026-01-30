# TDD — Minimal AI Voice Dictation (macOS, Push-to-Talk, Whisper.cpp + Cloud Rewriter)

**Goal:** A lightweight, personal dictation tool on macOS (no Electron, no Swift) that uses:

* **Local ASR**: `whisper.cpp` (fast, private for audio)
* **AI formatting**: a **cloud LLM** to rewrite into **Email mode** or **Message mode**
* **Push-to-talk**: hold a key to record, release to transcribe + rewrite + paste

---

## 1) Requirements

### Functional

* Push-to-talk (hold key):

  * On keydown: start recording
  * On keyup: stop recording and process
* Two output modes:

  * **Email**: professional, complete sentences, nice punctuation/paragraphs
  * **Message**: casual, short, conversational
* Output behavior:

  * Always copy to clipboard
  * Optional: auto-paste into the focused app
* Runs as a lightweight background app:

  * Either “script you run” OR a packaged `.app` you can launch at login
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

### Minimal UI (optional)

* v1: none (CLI logs)
* v2: menubar via `rumps` (still no Swift, still light)

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

   * Stores current mode (`email` / `message`)
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
* `MODE=email` (default)
* `AUTO_PASTE=false`
* `WHISPER_BIN=whisper-cpp`
* `WHISPER_MODEL_PATH=~/models/whisper/ggml-base.en.bin`
* `PTT_KEY=alt_r` (or `f18`)

### Defaults

* Start in `message` mode if you’re mostly chatting; otherwise `email`.
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

### Phase 5 — UI Overlay + Audio Feedback

Visual and audio feedback when dictating:

#### UI Features
* **Recording overlay**: Shows waveform/visualization when recording
* **Processing indicator**: Animation while transcribing/formatting
* **Audio feedback**: Sound cues on start/stop recording
* **Settings panel**: Configure mode, auto-paste, hotkey, etc.
* **Draggable panel**: Movable overlay that stays on top

#### Technology Options (Research)

| Option | Pros | Cons |
|--------|------|------|
| **Electron + React** | Full control, modern UI, rich ecosystem (e.g., OpenWhispr uses this) | Heavy (~100MB), separate JS stack |
| **pywebview** | Python-first, native webview, lightweight, bundler-friendly | Limited native integration |
| **NiceGUI** | Pure Python, browser-based, Vue.js UI, real-time updates | Runs web server, less "native" feel |
| **Tkinter/CustomTkinter** | Built-in, no extra deps, native look | Dated look, limited animation support |
| **PyQt6/PySide6** | Full native UI, rich widgets, good theming | Larger dependency, complex licensing |

#### Recommended: pywebview + HTML/CSS/JS

* Stays Python-centric (matches existing codebase)
* Modern UI via web technologies (CSS animations, waveform canvas)
* Lightweight (~5MB vs ~100MB for Electron)
* Can create floating transparent windows
* Bundler-friendly with py2app

#### UX Patterns (from Superwhisper/OpenWhispr)

1. **Press hotkey** → play "start" sound → show overlay with waveform
2. **While recording** → animate waveform based on audio amplitude
3. **Release hotkey** → play "stop" sound → show processing spinner
4. **Done** → flash success indicator → hide overlay OR show text preview
5. **Draggable** → user can reposition the overlay anywhere on screen

#### Implementation Plan

1. Create `ui/` directory with HTML/CSS/JS for overlay
2. Add `DictationWindow` class using pywebview
3. Integrate waveform visualization using Web Audio API or canvas
4. Add audio feedback sounds (bundled WAV files)
5. Create settings panel (mode toggle, auto-paste, hotkey config)
6. Communicate between Python ↔ JS via pywebview bridge

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
pip install sounddevice numpy pynput python-dotenv requests scipy
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