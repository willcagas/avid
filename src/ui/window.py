# window.py
"""Pywebview-based overlay window for dictation feedback."""

import queue
import threading
from collections.abc import Callable
from pathlib import Path

import webview

# Path to web assets
WEB_DIR = Path(__file__).parent / "web"


class Api:
    """JavaScript API bridge for the overlay window."""

    def __init__(self, on_mode_change: Callable | None = None,
                 on_auto_paste_change: Callable | None = None):
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

    def set_ui_state(self, state: str) -> None:
        """Request window resize based on UI state ('idle' or 'expanded')."""
        if hasattr(self, '_on_ui_state_change') and self._on_ui_state_change:
            self._on_ui_state_change(state)


class DictationWindow:
    """
    Manages the pywebview overlay window for dictation feedback.
    
    Shows waveform during recording, processing spinner, and success indicator.
    
    Note: On macOS, webview.start() must be called from the main thread.
    Use run_on_main_thread() to start the webview event loop.
    """

    def __init__(self,
                 mode: str = "email",
                 auto_paste: bool = False,
                 on_mode_change: Callable[[str], None] | None = None,
                 on_auto_paste_change: Callable[[bool], None] | None = None):
        """
        Initialize the dictation overlay window.
        
        Args:
            mode: Initial mode ("email" or "message")
            auto_paste: Initial auto-paste setting
            on_mode_change: Callback when mode changes via UI
            on_auto_paste_change: Callback when auto-paste changes via UI
        """
        self._api = Api(on_mode_change, on_auto_paste_change)
        # Link API callback to window method
        self._api._on_ui_state_change = self._handle_ui_state_change
        self._api.update_state(mode, auto_paste)

        self._window: webview.Window | None = None
        self._command_queue: queue.Queue = queue.Queue()
        self._ready = threading.Event()
        self._screen_width = 1920
        self._screen_height = 1080

    def _handle_ui_state_change(self, state: str) -> None:
        """Resize and reposition window based on UI state within current screen bounds."""
        if not self._window:
            return

        try:
            # Get current geometry
            curr_x = self._window.x
            curr_y = self._window.y
            curr_w = self._window.width
            curr_h = self._window.height

            # Fallback for platforms not reporting geometry?
            if curr_x is None:
                curr_x = 0
            if curr_y is None:
                curr_y = 0
            # On creation, width/height should be valid
        except Exception:
            # If getting geometry fails, abort resizing relative to center
            # and just fallback to bottom center default?
            # For now, let's try to proceed carefully.
            curr_x, curr_y = 0, 0
            curr_w, curr_h = 60, 60

        # Calculate center
        center_x = curr_x + (curr_w // 2)
        center_y = curr_y + (curr_h // 2)

        if state == 'idle':
            new_w, new_h = 60, 60
        else: # expanded
            new_w, new_h = 260, 80

        # Calculate new top-left to preserve center
        new_x = center_x - (new_w // 2)
        new_y = center_y - (new_h // 2)

        # Clamp to screen bounds with padding
        padding = 10
        max_x = self._screen_width - new_w - padding
        max_y = self._screen_height - new_h - padding

        new_x = max(padding, min(new_x, max_x))
        new_y = max(padding, min(new_y, max_y))

        self._window.resize(new_w, new_h)
        self._window.move(int(new_x), int(new_y))

    def _process_commands(self) -> None:
        """Process queued JS commands (called from webview thread)."""
        while True:
            try:
                cmd = self._command_queue.get_nowait()
                if cmd and self._window:
                    self._window.evaluate_js(cmd)
            except queue.Empty:
                break

    def _on_loaded(self) -> None:
        """Called when the webview page is loaded."""
        self._ready.set()

    def create_window(self) -> None:
        """Create the webview window. Must be called before start()."""
        # Get screen dimensions to position at bottom center
        try:
            from AppKit import NSScreen
            screen = NSScreen.mainScreen()
            screen_width = int(screen.frame().size.width)
            screen_height = int(screen.frame().size.height)
        except Exception:
            # Fallback dimensions
            screen_width = 1920
            screen_height = 1080

        self._screen_width = screen_width
        self._screen_height = screen_height

        # Start small (idle)
        window_width = 60
        window_height = 60
        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 30  # 30px from bottom

        self._window = webview.create_window(
            title='AI Voice Dictation',
            url=str(WEB_DIR / "index.html"),
            width=window_width,
            height=window_height,
            x=x,
            y=y,
            frameless=True,
            on_top=True,
            transparent=True,
            resizable=False,
            js_api=self._api,
            hidden=False  # Start visible (idle state)
        )
        self._window.events.loaded += self._on_loaded

    def start(self) -> None:
        """
        Start the webview event loop.
        
        IMPORTANT: This must be called from the main thread on macOS!
        This call blocks until the window is closed.
        """
        if self._window is None:
            self.create_window()

        # Start the webview - this blocks!
        webview.start(debug=False)

    def _queue_js(self, js: str) -> None:
        """Queue a JS command to be executed."""
        self._command_queue.put(js)
        # Trigger processing on the webview thread
        if self._window:
            try:
                self._window.evaluate_js("null")  # Wake up the event loop
                self._process_commands()
            except Exception:
                pass

    def show_recording(self) -> None:
        """Show the overlay with recording state."""
        if self._window:
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
        """Flash success indicator then return to idle."""
        if self._window:
            self._window.evaluate_js("showSuccess()")

    def hide(self) -> None:
        """Return to idle state (mic icon)."""
        if self._window:
            self._window.evaluate_js("showIdle()")

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
