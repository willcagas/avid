#!/bin/bash
# reload.sh
# Restarts the AViD LaunchAgent to apply code changes.

SERVICE_NAME="com.user.avid"

echo "♻️  Reloading AViD..."

# Stop the service (KeepAlive in plist should restart it, but we can be explicit)
# 'kickstart -k' kills and restarts the service
if launchctl list | grep -q "$SERVICE_NAME"; then
    # Use kickstart if available (macOS 10.11+) or fallback
    if command -v launchctl >/dev/null 2>&1; then
        # Try kickstart for current user context
        launchctl kickstart -k "gui/$(id -u)/$SERVICE_NAME" 2>/dev/null || \
        (launchctl stop "$SERVICE_NAME" && launchctl start "$SERVICE_NAME")
    else
        echo "Error: launchctl not found."
        exit 1
    fi
    echo "✅ Service restarted."
else
    echo "⚠️  Service not running or not installed. Attempting to start..."
    launchctl start "$SERVICE_NAME" || echo "Failed to start. Have you installed with scripts/install_launchagent.sh?"
fi
