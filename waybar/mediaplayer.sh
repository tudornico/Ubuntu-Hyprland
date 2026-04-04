#!/bin/bash

while true; do
    player=$(playerctl -l 2>/dev/null | while read p; do
        [ "$(playerctl -p "$p" status 2>/dev/null)" = "Playing" ] && echo "$p" && break
    done)

    if [ -n "$player" ]; then
        artist=$(playerctl -p "$player" metadata artist 2>/dev/null | sed 's/&/\&amp;/g')
        title=$(playerctl -p "$player" metadata title 2>/dev/null | sed 's/&/\&amp;/g')
        printf '{"text": "♪  %s — %s", "class": "playing"}\n' "$title" "$artist" || exit 0
    else
        printf '{"text": "", "class": "stopped"}\n' || exit 0
    fi
    sleep 3
done
