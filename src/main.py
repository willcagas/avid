# main.py
"""
Main entry point for the AI Voice Dictation application.

Orchestrates all components:
- HotkeyListener: Detects PTT key down/up
- AudioRecorder: Records audio while PTT is held
- Transcriber: Converts audio to text via whisper.cpp
- Formatter: Rewrites transcript via cloud LLM
- Injector: Copies to clipboard and optionally pastes
- DictationWindow: UI overlay for visual feedback (optional)
"""

import argparse
import signal
import sys
import threading

from .audio import AudioRecorder
from .config import Config
from .format_llm import Formatter
from .hotkeys import HotkeyListener
from .inject import Injector
from .transcribe import Transcriber
from .utils import get_temp_audio_path, setup_logging

logger = setup_logging()


class DictationApp:
    """Main application orchestrating all dictation components."""

    def __init__(self, use_ui: bool = False):
        """
        Initialize all components.
        
        Args:
            use_ui: Whether to show the UI overlay
        """
        logger.info("Initializing AI Voice Dictation...")

        self.config = Config()
        self.audio = AudioRecorder()
        self.transcriber = Transcriber(self.config)
        self.formatter = Formatter(self.config)
        self.injector = Injector()

        self.hotkey_listener: HotkeyListener | None = None
        self._running = False
        self._use_ui = use_ui
        self._ui = None  # Type: DictationWindow (lazy import in run_with_ui)
        self._play_start_sound = lambda: None
        self._play_stop_sound = lambda: None

        # For tracking amplitude during recording
        self._amplitude_thread: threading.Thread | None = None
        self._recording = False

    def _update_amplitude(self) -> None:
        """Update UI with audio amplitude while recording."""
        import time
        while self._recording and self._ui:
            amplitude = self.audio.get_amplitude()
            self._ui.update_waveform(amplitude)
            time.sleep(0.05)  # 20 FPS

    def on_ptt_press(self) -> None:
        """Handle PTT key press - start recording."""
        logger.info("🎤 Recording...")

        # Play start sound and show UI
        if self._use_ui:
            self._play_start_sound()
            if self._ui:
                self._ui.show_recording()

        # Start recording
        self.audio.start_recording()
        self._recording = True

        # Start amplitude tracking for UI
        if self._ui:
            # Ensure previous thread is cleaned up
            if self._amplitude_thread and self._amplitude_thread.is_alive():
                self._recording = False
                self._amplitude_thread.join(timeout=1.0)

            self._amplitude_thread = threading.Thread(
                target=self._update_amplitude,
                daemon=True
            )
            self._amplitude_thread.start()

    def on_ptt_release(self) -> None:
        """Handle PTT key release - process audio pipeline."""
        self._recording = False
        
        # Wait for amplitude thread to finish
        if self._amplitude_thread and self._amplitude_thread.is_alive():
            self._amplitude_thread.join(timeout=1.0)

        temp_path = get_temp_audio_path()

        # Play stop sound
        if self._use_ui:
            self._play_stop_sound()

        # Stop recording and save audio
        if not self.audio.stop_recording(temp_path):
            logger.warning("No audio recorded")
            if self._ui:
                self._ui.hide()
            return

        # Show processing state
        if self._ui:
            self._ui.show_processing()

        # Transcribe audio
        logger.info("📝 Transcribing...")
        raw_text = self.transcriber.transcribe(temp_path)

        if not raw_text or not raw_text.strip():
            logger.warning("No transcript produced")
            if self._ui:
                self._ui.hide()
            return

        logger.info(f"Raw: {raw_text[:100]}...")

        # Skip formatter for very short transcripts (likely noise/blank)
        if len(raw_text.strip()) < 3:
            logger.info("Transcript too short, skipping formatter")
            formatted_text = raw_text.strip()
        else:
            # Format with LLM
            logger.info(f"✨ Formatting ({self.config.mode} mode)...")
            formatted_text = self.formatter.format(raw_text, self.config.mode)

        logger.info(f"Formatted: {formatted_text[:100]}...")

        # Inject to clipboard (and optionally paste)
        logger.info("📋 Copying to clipboard...")
        self.injector.inject(formatted_text, self.config.auto_paste)

        # Show success
        if self._ui:
            self._ui.show_success()

        logger.info("✅ Done!")

    def _run_hotkey_listener(self) -> None:
        """Run the hotkey listener in a background thread."""
        self.hotkey_listener = HotkeyListener(
            ptt_key=self.config.ptt_key,
            on_press=self.on_ptt_press,
            on_release=self.on_ptt_release
        )
        self.hotkey_listener.start()
        self.hotkey_listener.wait()

    def run(self) -> None:
        """Start the application main loop (CLI mode)."""
        self._running = True

        # Set up hotkey listener
        self.hotkey_listener = HotkeyListener(
            ptt_key=self.config.ptt_key,
            on_press=self.on_ptt_press,
            on_release=self.on_ptt_release
        )

        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            logger.info("\nShutting down...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start listening
        self.hotkey_listener.start()

        logger.info("=" * 50)
        logger.info("AI Voice Dictation is running!")
        logger.info(f"Mode: {self.config.mode}")
        logger.info(f"PTT Key: {self.config.ptt_key}")
        logger.info(f"Auto-paste: {self.config.auto_paste}")
        logger.info("=" * 50)
        logger.info("Hold PTT key to record, release to process.")
        logger.info("Press Ctrl+C to quit.")

        # Block until stopped
        self.hotkey_listener.wait()

    def run_with_ui(self) -> None:
        """Start the application with UI overlay (webview on main thread)."""
        from .ui import DictationWindow, play_start_sound, play_stop_sound

        self._running = True
        self._play_start_sound = play_start_sound
        self._play_stop_sound = play_stop_sound

        # Helper to update mode from UI
        def on_mode_change(new_mode: str) -> None:
            self.config.mode = new_mode
            logger.info(f"Mode switched to: {new_mode}")

        # Create UI window
        self._ui = DictationWindow(
            mode=self.config.mode,
            auto_paste=self.config.auto_paste,
            on_mode_change=on_mode_change
        )
        self._ui.create_window()

        # Start hotkey listener in background thread
        hotkey_thread = threading.Thread(
            target=self._run_hotkey_listener,
            daemon=True
        )
        hotkey_thread.start()

        logger.info("=" * 50)
        logger.info("AI Voice Dictation is running (UI mode)!")
        logger.info(f"Mode: {self.config.mode}")
        logger.info(f"PTT Key: {self.config.ptt_key}")
        logger.info(f"Auto-paste: {self.config.auto_paste}")
        logger.info("=" * 50)
        logger.info("Hold PTT key to record, release to process.")
        logger.info("Close the overlay window to quit.")

        # Run webview on main thread (this blocks!)
        self._ui.start()

    def stop(self) -> None:
        """Stop the application."""
        self._running = False
        self._recording = False
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self._ui:
            self._ui.destroy()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Voice Dictation")
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Enable UI overlay with waveform and visual feedback"
    )
    args = parser.parse_args()

    app = DictationApp(use_ui=args.ui)

    if args.ui:
        app.run_with_ui()
    else:
        app.run()


if __name__ == "__main__":
    main()
