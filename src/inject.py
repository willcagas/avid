# inject.py
"""
Injector component for outputting formatted text.

Copies text to clipboard (always) and optionally pastes via ⌘V.
"""

import subprocess
import time

from .utils import setup_logging

logger = setup_logging()


class Injector:
    """Injects text into clipboard and optionally pastes."""

    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to the macOS clipboard using pbcopy.
        
        Args:
            text: Text to copy
        
        Returns:
            True if successful, False otherwise
        """
        try:
            process = subprocess.Popen(
                ["pbcopy"],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=text)

            if process.returncode == 0:
                logger.info(f"Copied to clipboard: {len(text)} chars")
                return True
            else:
                logger.error("pbcopy failed")
                return False

        except FileNotFoundError:
            logger.error("pbcopy not found - this tool requires macOS")
            return False
        except Exception as e:
            logger.error(f"Clipboard error: {e}")
            return False

    def paste(self) -> bool:
        """
        Simulate ⌘V paste using osascript.
        
        Requires Accessibility permissions for the running app.
        
        Returns:
            True if successful, False otherwise
        """
        script = '''
        tell application "System Events"
            keystroke "v" using command down
        end tell
        '''

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                logger.info("Paste triggered")
                return True
            else:
                logger.error(f"Paste failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Paste timed out")
            return False
        except Exception as e:
            logger.error(f"Paste error: {e}")
            return False

    def inject(self, text: str, auto_paste: bool = False) -> bool:
        """
        Inject text: copy to clipboard and optionally paste.
        
        Args:
            text: Text to inject
            auto_paste: Whether to also trigger paste
        
        Returns:
            True if clipboard copy succeeded
        """
        success = self.copy_to_clipboard(text)

        if success and auto_paste:
            # Small delay to ensure clipboard is ready
            time.sleep(0.1)
            self.paste()

        return success
