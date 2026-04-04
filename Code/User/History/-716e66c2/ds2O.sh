#!/bin/bash

# Ensure cava config exists
CONFIG_FILE="$HOME/.config/cava/config_waybar"

# Clean up cava on exit
trap "pkill -P $$" EXIT

# Use stdbuf to prevent data from getting stuck in the pipe
# We use 'tr' and 'sed' to map the 0-7 range to Unicode blocks
stdbuf -oL cava -p "$CONFIG_FILE" | stdbuf -oL tr '01234567' ' ▂▃▄▅▆▇█'