# hotkeys.py
"""
HotkeyListener component for push-to-talk functionality.

Uses pynput to detect global key press/release events for PTT.
"""

from typing import Callable, Optional, Union

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from .utils import setup_logging

logger = setup_logging()

# Mapping of key names to pynput Key objects
KEY_MAP = {
    # Special keys
    "alt_r": Key.alt_r,
    "alt_l": Key.alt_l,
    "ctrl_r": Key.ctrl_r,
    "ctrl_l": Key.ctrl_l,
    "shift_r": Key.shift_r,
    "shift_l": Key.shift_l,
    "cmd_r": Key.cmd_r,
    "cmd_l": Key.cmd_l,
    # Function keys
    "f1": Key.f1,
    "f2": Key.f2,
    "f3": Key.f3,
    "f4": Key.f4,
    "f5": Key.f5,
    "f6": Key.f6,
    "f7": Key.f7,
    "f8": Key.f8,
    "f9": Key.f9,
    "f10": Key.f10,
    "f11": Key.f11,
    "f12": Key.f12,
    "f13": Key.f13,
    "f14": Key.f14,
    "f15": Key.f15,
    "f16": Key.f16,
    "f17": Key.f17,
    "f18": Key.f18,
    "f19": Key.f19,
    "f20": Key.f20,
}


class HotkeyListener:
    """Listens for push-to-talk key press/release events."""
    
    def __init__(
        self,
        ptt_key: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ):
        """
        Initialize the hotkey listener.
        
        Args:
            ptt_key: Key name (e.g., "alt_r", "f18")
            on_press: Callback for key press
            on_release: Callback for key release
        """
        self.ptt_key = self._resolve_key(ptt_key)
        self.ptt_key_name = ptt_key
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        
        self._listener: Optional[keyboard.Listener] = None
        self._key_held = False
    
    def _resolve_key(self, key_name: str) -> Union[Key, KeyCode]:
        """Resolve key name to pynput Key or KeyCode."""
        key_lower = key_name.lower()
        
        if key_lower in KEY_MAP:
            return KEY_MAP[key_lower]
        
        # Single character key
        if len(key_name) == 1:
            return KeyCode.from_char(key_name)
        
        logger.warning(f"Unknown key '{key_name}', defaulting to alt_r")
        return Key.alt_r
    
    def _matches_ptt_key(self, key: Union[Key, KeyCode]) -> bool:
        """Check if the pressed key matches the PTT key."""
        return key == self.ptt_key
    
    def _on_press(self, key: Union[Key, KeyCode, None]) -> None:
        """Handle key press events."""
        if key is None:
            return
            
        if self._matches_ptt_key(key) and not self._key_held:
            self._key_held = True
            logger.debug(f"PTT key pressed: {self.ptt_key_name}")
            try:
                self.on_press_callback()
            except Exception as e:
                logger.error(f"Error in on_press callback: {e}")
    
    def _on_release(self, key: Union[Key, KeyCode, None]) -> None:
        """Handle key release events."""
        if key is None:
            return
            
        if self._matches_ptt_key(key) and self._key_held:
            self._key_held = False
            logger.debug(f"PTT key released: {self.ptt_key_name}")
            try:
                self.on_release_callback()
            except Exception as e:
                logger.error(f"Error in on_release callback: {e}")
    
    def start(self) -> None:
        """Start listening for hotkey events."""
        if self._listener is not None:
            logger.warning("Listener already running")
            return
        
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        logger.info(f"Hotkey listener started (PTT key: {self.ptt_key_name})")
    
    def stop(self) -> None:
        """Stop listening for hotkey events."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey listener stopped")
    
    def wait(self) -> None:
        """Wait for the listener to finish (blocking)."""
        if self._listener is not None:
            self._listener.join()
