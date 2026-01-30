#!/bin/bash
# install_launchagent.sh
# Installs the LaunchAgent plist to start AI Voice Dictation at login

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.user.aidictation.plist"
PLIST_SOURCE="$PROJECT_DIR/launchd/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Installing LaunchAgent for AI Voice Dictation..."

# Check if plist source exists
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "Error: Plist file not found at $PLIST_SOURCE"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Unload existing agent if present
if [ -f "$PLIST_DEST" ]; then
    echo "Unloading existing agent..."
    launchctl unload "$PLIST_DEST" 2>/dev/null
fi

# Copy plist to LaunchAgents
echo "Copying plist to $PLIST_DEST..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# Update plist with actual project path
sed -i '' "s|/path/to/ai-dictation|$PROJECT_DIR|g" "$PLIST_DEST"

# Load the agent
echo "Loading agent..."
launchctl load "$PLIST_DEST"

echo "Done! AI Voice Dictation will now start at login."
echo "To start immediately: launchctl start com.user.aidictation"
echo "To stop: launchctl stop com.user.aidictation"
echo "To uninstall: launchctl unload $PLIST_DEST && rm $PLIST_DEST"
