#!/bin/bash

# Find playing player
player=$(playerctl -l 2>/dev/null | while read p; do
    [ "$(playerctl -p "$p" status 2>/dev/null)" = "Playing" ] && echo "$p" && break
done)

# Colors (Tokyo Night)
CYAN='\033[38;2;125;207;255m'
VIOLET='\033[38;2;187;154;247m'
BLUE='\033[38;2;122;162;247m'
DIM='\033[38;2;86;95;137m'
BOLD='\033[1m'
RESET='\033[0m'

clear
if [ -z "$player" ]; then
    echo -e "${DIM}  nothing playing${RESET}"
    sleep 2
    exit 0
fi

# Print track info header (refreshes every 3s in background loop)
print_info() {
    while true; do
        artist=$(playerctl -p "$player" metadata artist 2>/dev/null)
        title=$(playerctl -p "$player" metadata title 2>/dev/null)
        tput cup 0 0
        echo -e "${CYAN}${BOLD}  $title${RESET}"
        echo -e "${VIOLET}  $artist${RESET}"
        echo -e "${DIM}─────────────────────────────────────────${RESET}"
        sleep 3
    done
}

print_info &
INFO_PID=$!

# Run cava below the header (offset 3 lines down)
tput cup 3 0
cava

kill $INFO_PID 2>/dev/null
