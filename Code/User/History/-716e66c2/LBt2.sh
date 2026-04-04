#!/bin/bash
pkill -x cava
sleep 0.1

# 'tr' is much faster than 'sed' for simple character swapping.
# This version swaps 0-7 into blocks and nukes the newline/separator issues.
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | stdbuf -i0 -o0 -e0 tr '01234567' ' ▂▃▄▅▆▇█'