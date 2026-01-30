# menubar.py
"""
Menubar application for AI Voice Dictation using rumps.

Provides a lightweight macOS menu bar interface for:
- Toggling between Email/Message modes
- Toggling auto-paste on/off
- Showing recording/processing status
- Quitting the application
"""

from typing import Callable, Optional
import rumps

from .utils import setup_logging

logger = setup_logging()

# Menu bar icons (using emoji for simplicity)
ICON_IDLE = "🎤"
ICON_RECORDING = "🔴"
ICON_PROCESSING = "⏳"


class MenubarApp(rumps.App):
    """Menubar application for AI Voice Dictation."""
    
    def __init__(
        self,
        mode: str = "email",
        auto_paste: bool = False,
        on_mode_change: Optional[Callable[[str], None]] = None,
        on_auto_paste_change: Optional[Callable[[bool], None]] = None,
        on_quit: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the menubar app.
        
        Args:
            mode: Initial mode ("email" or "message")
            auto_paste: Initial auto-paste setting
            on_mode_change: Callback when mode changes
            on_auto_paste_change: Callback when auto-paste changes
            on_quit: Callback when quit is selected
        """
        super().__init__(ICON_IDLE, quit_button=None)
        
        self._mode = mode
        self._auto_paste = auto_paste
        self._on_mode_change = on_mode_change
        self._on_auto_paste_change = on_auto_paste_change
        self._on_quit = on_quit
        
        # Build menu
        self._build_menu()
    
    def _build_menu(self) -> None:
        """Build the menu items."""
        # Mode submenu
        self.mode_email = rumps.MenuItem(
            "Email",
            callback=self._set_email_mode
        )
        self.mode_message = rumps.MenuItem(
            "Message", 
            callback=self._set_message_mode
        )
        self._update_mode_checkmarks()
        
        mode_menu = rumps.MenuItem("Mode")
        mode_menu.add(self.mode_email)
        mode_menu.add(self.mode_message)
        
        # Auto-paste toggle
        self.auto_paste_item = rumps.MenuItem(
            "Auto-paste",
            callback=self._toggle_auto_paste
        )
        self.auto_paste_item.state = self._auto_paste
        
        # Separator and quit
        separator = rumps.separator
        quit_item = rumps.MenuItem("Quit", callback=self._quit)
        
        # Add all items
        self.menu = [
            mode_menu,
            self.auto_paste_item,
            separator,
            quit_item
        ]
    
    def _update_mode_checkmarks(self) -> None:
        """Update checkmarks on mode menu items."""
        self.mode_email.state = (self._mode == "email")
        self.mode_message.state = (self._mode == "message")
    
    def _set_email_mode(self, _) -> None:
        """Switch to email mode."""
        if self._mode != "email":
            self._mode = "email"
            self._update_mode_checkmarks()
            logger.info("Mode changed to: email")
            if self._on_mode_change:
                self._on_mode_change("email")
    
    def _set_message_mode(self, _) -> None:
        """Switch to message mode."""
        if self._mode != "message":
            self._mode = "message"
            self._update_mode_checkmarks()
            logger.info("Mode changed to: message")
            if self._on_mode_change:
                self._on_mode_change("message")
    
    def _toggle_auto_paste(self, sender: rumps.MenuItem) -> None:
        """Toggle auto-paste setting."""
        self._auto_paste = not self._auto_paste
        sender.state = self._auto_paste
        logger.info(f"Auto-paste: {'on' if self._auto_paste else 'off'}")
        if self._on_auto_paste_change:
            self._on_auto_paste_change(self._auto_paste)
    
    def _quit(self, _) -> None:
        """Quit the application."""
        logger.info("Quit requested from menubar")
        if self._on_quit:
            self._on_quit()
        rumps.quit_application()
    
    # Public methods for status updates
    def set_recording(self) -> None:
        """Set icon to recording state."""
        self.title = ICON_RECORDING
    
    def set_processing(self) -> None:
        """Set icon to processing state."""
        self.title = ICON_PROCESSING
    
    def set_idle(self) -> None:
        """Set icon to idle state."""
        self.title = ICON_IDLE
    
    @property
    def mode(self) -> str:
        """Get current mode."""
        return self._mode
    
    @property
    def auto_paste(self) -> bool:
        """Get current auto-paste setting."""
        return self._auto_paste
