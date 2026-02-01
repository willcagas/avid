
import Cocoa
import sys
from pathlib import Path

def set_file_icon(file_path, icon_path):
    """Set the custom icon for a file using NSWorkspace."""
    image = Cocoa.NSImage.alloc().initByReferencingFile_(str(icon_path))
    if not image or not image.isValid():
        print(f"Error: Invalid or missing icon at {icon_path}")
        return False
    
    success = Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(image, str(file_path), 0)
    return success

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Default behavior for AViD project
        base = Path.cwd()
        target = base / "Launch AViD.command"
        icon = base / "assets/avid_logo.png"
    else:
        target = Path(sys.argv[1])
        icon = Path(sys.argv[2])

    print(f"Target: {target}")
    print(f"Icon: {icon}")

    if not target.exists():
        print("Target file not found.")
        sys.exit(1)
        
    if not icon.exists():
        print("Icon file not found.")
        sys.exit(1)

    if set_file_icon(target, icon):
        print("Icon set successfully!")
    else:
        print("Failed to set icon.")
