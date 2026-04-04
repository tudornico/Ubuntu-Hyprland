#!/bin/bash

# Kill all previous instances to clear the "pipe"
pkill -x cava
sleep 0.1

# 1. 'stdbuf -i0 -o0 -e0' completely disables buffering (Input/Output/Error)
# 2. 'sed -u' processes the stream instantly as it arrives
# 3. We use a shorter translation string to speed up the CPU
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-6]//g;s/0/ /g;s/1/▂/g;s/2/▃/g;s/3/▄/g;s/4/▅/g;s/5/▆/g;s/6/█/g'