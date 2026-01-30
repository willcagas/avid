# window.py
"""Pywebview-based overlay window for dictation feedback."""

import webview
import threading
from pathlib import Path
from typing import Optional, Callable

# Path to web assets
WEB_DIR = Path(__file__).parent / "web"


class Api:
    """JavaScript API bridge for the overlay window."""
    
    def __init__(self, on_mode_change: Optional[Callable] = None,
                 on_auto_paste_change: Optional[Callable] = None):
        self._mode = "email"
        self._auto_paste = False
        self._on_mode_change = on_mode_change
        self._on_auto_paste_change = on_auto_paste_change
    
    def get_state(self) -> dict:
        """Get current app state for the UI."""
        return {
            "mode": self._mode,
            "auto_paste": self._auto_paste
        }
    
    def set_mode(self, mode: str) -> None:
        """Set the current mode."""
        self._mode = mode
        if self._on_mode_change:
            self._on_mode_change(mode)
    
    def set_auto_paste(self, enabled: bool) -> None:
        """Set auto-paste setting."""
        self._auto_paste = enabled
        if self._on_auto_paste_change:
            self._on_auto_paste_change(enabled)
    
    def update_state(self, mode: str, auto_paste: bool) -> None:
        """Update internal state (called from Python side)."""
        self._mode = mode
        self._auto_paste = auto_paste


class DictationWindow:
    """
    Manages the pywebview overlay window for dictation feedback.
    
    Shows waveform during recording, processing spinner, and success indicator.
    """
    
    def __init__(self, 
                 mode: str = "email",
                 auto_paste: bool = False,
                 on_mode_change: Optional[Callable[[str], None]] = None,
                 on_auto_paste_change: Optional[Callable[[bool], None]] = None):
        """
        Initialize the dictation overlay window.
        
        Args:
            mode: Initial mode ("email" or "message")
            auto_paste: Initial auto-paste setting
            on_mode_change: Callback when mode changes via UI
            on_auto_paste_change: Callback when auto-paste changes via UI
        """
        self._api = Api(on_mode_change, on_auto_paste_change)
        self._api.update_state(mode, auto_paste)
        
        self._window: Optional[webview.Window] = None
        self._started = threading.Event()
    
    def _create_window(self) -> None:
        """Create the webview window (called from webview thread)."""
        self._window = webview.create_window(
            title='AI Voice Dictation',
            url=str(WEB_DIR / "index.html"),
            width=320,
            height=100,
            x=100,
            y=100,
            frameless=True,
            on_top=True,
            transparent=True,
            resizable=False,
            js_api=self._api,
            hidden=True  # Start hidden
        )
        self._started.set()
    
    def start(self) -> None:
        """
        Start the webview in a background thread.
        
        This must be called before any other window methods.
        """
        def run_webview():
            self._create_window()
            webview.start(debug=False)
        
        thread = threading.Thread(target=run_webview, daemon=True)
        thread.start()
        
        # Wait for window to be created
        self._started.wait(timeout=5.0)
    
    def show_recording(self) -> None:
        """Show the overlay with recording state."""
        if self._window:
            self._window.show()
            self._window.evaluate_js("showRecording()")
    
    def update_waveform(self, amplitude: float) -> None:
        """
        Update the waveform visualization with current amplitude.
        
        Args:
            amplitude: Audio amplitude (0.0 to 1.0)
        """
        if self._window:
            self._window.evaluate_js(f"updateWaveform({amplitude})")
    
    def show_processing(self) -> None:
        """Show the processing spinner."""
        if self._window:
            self._window.evaluate_js("showProcessing()")
    
    def show_success(self) -> None:
        """Flash success indicator then hide."""
        if self._window:
            self._window.evaluate_js("showSuccess()")
    
    def hide(self) -> None:
        """Hide the overlay window."""
        if self._window:
            self._window.hide()
    
    def update_mode(self, mode: str) -> None:
        """Update the mode in the UI."""
        self._api._mode = mode
        if self._window:
            self._window.evaluate_js(f"updateMode('{mode}')")
    
    def update_auto_paste(self, auto_paste: bool) -> None:
        """Update the auto-paste setting in the UI."""
        self._api._auto_paste = auto_paste
        if self._window:
            self._window.evaluate_js(f"updateAutoPaste({str(auto_paste).lower()})")
    
    def destroy(self) -> None:
        """Destroy the window."""
        if self._window:
            self._window.destroy()
