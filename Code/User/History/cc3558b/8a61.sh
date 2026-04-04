#!/bin/bash

BLOCKS=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")
FIFO=/tmp/cava-waybar

# Create named pipe if it doesn't exist
[ -p "$FIFO" ] || mkfifo "$FIFO"

# Start cava if not running
pgrep -x cava > /dev/null || cava -p ~/.config/cava/waybar-config &

# Read cava in background, keep only latest value
LATEST=""
exec 3<>"$FIFO"
while IFS= read -r line <&3; do
    LATEST="$line"
done &
READER_PID=$!

cleanup() {
    kill $READER_PID 2>/dev/null
    pkill -x cava 2>/dev/null
    exec 3>&-
    exit 0
}
trap cleanup EXIT INT TERM

while true; do
    player=$(playerctl -l 2>/dev/null | while read p; do
        [ "$(playerctl -p "$p" status 2>/dev/null)" = "Playing" ] && echo "$p" && break
    done)

    if [ -n "$player" ]; then
        artist=$(playerctl -p "$player" metadata artist 2>/dev/null)
        title=$(playerctl -p "$player" metadata title 2>/dev/null)

        bar=""
        for val in $LATEST; do
            idx=$((val > 7 ? 7 : val))
            bar+="${BLOCKS[$idx]}"
        done

        echo "{\"text\": \"${bar}  ${title} — ${artist}\", \"class\": \"playing\"}"
    else
        pkill -x cava 2>/dev/null
        echo "{\"text\": \"\", \"class\": \"stopped\"}"
    fi

    sleep 0.1
done