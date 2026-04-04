#!/bin/bash

# Terminate any existing cava processes to prevent conflicts
pkill -x cava

# Give it a tiny moment to breathe
sleep 0.5

# Run CAVA in a way that forces every line to be sent to Waybar immediately
# We use 'stdbuf -oL' to disable buffering
stdbuf -oL cava -p ~/.config/cava/config_waybar | stdbuf -oL tr '01234567' ' ▂▃▄▅▆▇█'