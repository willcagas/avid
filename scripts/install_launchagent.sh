#!/bin/bash
# install_launchagent.sh
# Installs the LaunchAgent plist to start AViD at login

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.user.avid.plist"
PLIST_SOURCE="$PROJECT_DIR/launchd/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Installing LaunchAgent for AViD..."

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
sed -i '' "s|/path/to/avid|$PROJECT_DIR|g" "$PLIST_DEST"

# Load the agent
echo "Loading agent..."
launchctl load "$PLIST_DEST"

echo "Done! AViD will now start at login."
echo "To start immediately: launchctl start com.user.avid"
echo "To stop: launchctl stop com.user.avid"
echo "To uninstall: launchctl unload $PLIST_DEST && rm $PLIST_DEST"
