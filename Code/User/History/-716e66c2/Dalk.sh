#!/bin/bash

# Kill existing cava
pkill -x cava

# 1. We use stdbuf to force the data through immediately
# 2. We use 'tr' to delete the semicolons
# 3. We use 'sed' with the '-u' (unbuffered) flag to translate numbers to blocks
# 4. We add a 'translate' for the newline so Waybar sees each "frame"
stdbuf -oL cava -p ~/.config/cava/config_waybar | stdbuf -oL tr -d ';' | sed -u 's/0/ /g; s/1/▂/g; s/2/▃/g; s/3/▄/g; s/4/▅/g; s/5/▆/g; s/6/▇/g; s/7/█/g'