#!/bin/bash
cd "$(dirname "$0")"

# Internal: If running in background mode, execute the python app
if [ "$1" == "--background" ]; then
    ./scripts/run.sh --ui
    exit
fi

# Main Entry:
# 1. Launch THIS script again in the background (detached)
nohup "$0" --background >/dev/null 2>&1 &

# 2. Smart Quit: Quit Terminal if this is the only window, otherwise just close it
osascript -e '
tell application "Terminal"
    if (count of windows) <= 1 then
        quit
    else
        close front window
    end if
end tell
' &
exit
