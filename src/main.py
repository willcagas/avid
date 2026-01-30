# main.py
"""
Main entry point for the AI Voice Dictation application.

Orchestrates all components:
- HotkeyListener: Detects PTT key down/up
- AudioRecorder: Records audio while PTT is held
- Transcriber: Converts audio to text via whisper.cpp
- Formatter: Rewrites transcript via cloud LLM
- Injector: Copies to clipboard and optionally pastes

Usage:
    python -m src.main           # CLI mode (default)
    python -m src.main --menubar # Menubar mode
"""

import argparse
import signal
import sys
import threading
from typing import Optional

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
    
    def __init__(self):
        """Initialize all components."""
        logger.info("Initializing AI Voice Dictation...")
        
        self.config = Config()
        self.audio = AudioRecorder()
        self.transcriber = Transcriber(self.config)
        self.formatter = Formatter(self.config)
        self.injector = Injector()
        
        self.hotkey_listener: Optional[HotkeyListener] = None
        self.menubar_app = None  # Set when running in menubar mode
        self._running = False
        
        # Runtime settings (can be changed via menubar)
        self._mode = self.config.mode
        self._auto_paste = self.config.auto_paste
    
    @property
    def mode(self) -> str:
        """Get current mode."""
        return self._mode
    
    @mode.setter
    def mode(self, value: str) -> None:
        """Set current mode."""
        self._mode = value
    
    @property
    def auto_paste(self) -> bool:
        """Get current auto-paste setting."""
        return self._auto_paste
    
    @auto_paste.setter
    def auto_paste(self, value: bool) -> None:
        """Set current auto-paste setting."""
        self._auto_paste = value
    
    def on_ptt_press(self) -> None:
        """Handle PTT key press - start recording."""
        logger.info("🎤 Recording...")
        if self.menubar_app:
            self.menubar_app.set_recording()
        self.audio.start_recording()
    
    def on_ptt_release(self) -> None:
        """Handle PTT key release - process audio pipeline."""
        if self.menubar_app:
            self.menubar_app.set_processing()
        
        temp_path = get_temp_audio_path()
        
        # Stop recording and save audio
        if not self.audio.stop_recording(temp_path):
            logger.warning("No audio recorded")
            if self.menubar_app:
                self.menubar_app.set_idle()
            return
        
        # Transcribe audio
        logger.info("📝 Transcribing...")
        raw_text = self.transcriber.transcribe(temp_path)
        
        if not raw_text:
            logger.warning("No transcript produced")
            if self.menubar_app:
                self.menubar_app.set_idle()
            return
        
        logger.info(f"Raw: {raw_text[:100]}...")
        
        # Format with LLM
        logger.info(f"✨ Formatting ({self._mode} mode)...")
        formatted_text = self.formatter.format(raw_text, self._mode)
        
        logger.info(f"Formatted: {formatted_text[:100]}...")
        
        # Inject to clipboard (and optionally paste)
        logger.info("📋 Copying to clipboard...")
        self.injector.inject(formatted_text, self._auto_paste)
        
        logger.info("✅ Done!")
        if self.menubar_app:
            self.menubar_app.set_idle()
    
    def _setup_hotkey_listener(self) -> None:
        """Set up the hotkey listener."""
        self.hotkey_listener = HotkeyListener(
            ptt_key=self.config.ptt_key,
            on_press=self.on_ptt_press,
            on_release=self.on_ptt_release
        )
        self.hotkey_listener.start()
    
    def run(self) -> None:
        """Start the application in CLI mode."""
        self._running = True
        
        # Set up hotkey listener
        self._setup_hotkey_listener()
        
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            logger.info("\nShutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("=" * 50)
        logger.info("AI Voice Dictation is running!")
        logger.info(f"Mode: {self._mode}")
        logger.info(f"PTT Key: {self.config.ptt_key}")
        logger.info(f"Auto-paste: {self._auto_paste}")
        logger.info("=" * 50)
        logger.info("Hold PTT key to record, release to process.")
        logger.info("Press Ctrl+C to quit.")
        
        # Block until stopped
        self.hotkey_listener.wait()
    
    def run_with_menubar(self) -> None:
        """Start the application with menubar UI."""
        # Import here to avoid requiring rumps for CLI mode
        from .menubar import MenubarApp
        
        self._running = True
        
        # Create menubar app with callbacks
        self.menubar_app = MenubarApp(
            mode=self._mode,
            auto_paste=self._auto_paste,
            on_mode_change=lambda m: setattr(self, 'mode', m),
            on_auto_paste_change=lambda a: setattr(self, 'auto_paste', a),
            on_quit=self.stop
        )
        
        # Start hotkey listener in background thread
        self._setup_hotkey_listener()
        
        logger.info("=" * 50)
        logger.info("AI Voice Dictation is running (menubar mode)!")
        logger.info(f"Mode: {self._mode}")
        logger.info(f"PTT Key: {self.config.ptt_key}")
        logger.info("=" * 50)
        
        # Run menubar (this blocks)
        self.menubar_app.run()
    
    def stop(self) -> None:
        """Stop the application."""
        self._running = False
        if self.hotkey_listener:
            self.hotkey_listener.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Voice Dictation")
    parser.add_argument(
        "--menubar",
        action="store_true",
        help="Run with menubar UI instead of CLI"
    )
    args = parser.parse_args()
    
    app = DictationApp()
    
    if args.menubar:
        app.run_with_menubar()
    else:
        app.run()


if __name__ == "__main__":
    main()
