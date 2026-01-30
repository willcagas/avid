# inject.py
"""
Injector component for outputting formatted text.

Responsibilities:
- Copy formatted text to clipboard (always)
- Optionally trigger paste via ⌘V (if AUTO_PASTE=true)

Clipboard:
- Uses pbcopy (macOS)

Auto-paste:
- Uses osascript to simulate ⌘V
- Requires Accessibility permission
"""

# TODO: Implement Injector class
# TODO: Implement copy_to_clipboard using subprocess + pbcopy
# TODO: Implement auto_paste using osascript
# TODO: Handle clipboard copy failure gracefully
# TODO: Log actions for debugging
