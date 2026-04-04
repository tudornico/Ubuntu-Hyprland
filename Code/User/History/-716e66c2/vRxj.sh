#!/bin/bash

# Kill old instances
pkill -x cava

# The actual command
stdbuf -oL cava -p ~/.config/cava/config_waybar | while read -r line; do
    # Replace numbers with blocks using 'sed'
    echo "$line" | sed 's/0/ /g; s/1/▂/g; s/2/▃/g; s/3/▄/g; s/4/▅/g; s/5/▆/g; s/6/▇/g; s/7/█/g'
done