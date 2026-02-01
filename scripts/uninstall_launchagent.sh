#!/bin/bash
# uninstall_launchagent.sh
# Removes the LaunchAgent for AViD

PLIST_NAME="com.user.avid.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Uninstalling LaunchAgent for AViD..."

# Check if plist exists
if [ ! -f "$PLIST_DEST" ]; then
    echo "LaunchAgent not installed (plist not found at $PLIST_DEST)"
    exit 0
fi

# Stop the agent if running
echo "Stopping agent..."
launchctl stop com.user.avid 2>/dev/null

# Unload the agent
echo "Unloading agent..."
launchctl unload "$PLIST_DEST" 2>/dev/null

# Remove the plist
echo "Removing plist..."
rm "$PLIST_DEST"

# Clean up log files (optional)
echo "Cleaning up log files..."
rm -f /tmp/avid.out.log /tmp/avid.err.log

echo "Done! AViD will no longer start at login."
