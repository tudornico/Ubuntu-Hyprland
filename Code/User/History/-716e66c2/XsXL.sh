#!/bin/bash

# Kill any existing cava instances
pkill -x cava

# Path to your cava config
CONFIG_FILE="$HOME/.config/cava/config_waybar"

# Ensure the config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config not found"
    exit 1
fi

# Run cava and translate numbers to blocks
# 'stdbuf' ensures the data flows instantly
# 'tr' maps 0-7 to the block characters
stdbuf -oL cava -p "$CONFIG_FILE" | stdbuf -oL tr '01234567' ' ▂▃▄▅▆▇█'