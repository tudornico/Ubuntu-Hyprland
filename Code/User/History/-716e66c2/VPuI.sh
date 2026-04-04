#!/bin/bash
pkill -x cava
sleep 0.1

# We map 0 to a space, but 1-7 to increasingly tall blocks.
# This ensures that even quiet parts have a "heartbeat" on the bar.
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-7]//g;s/0/ /g;s/1/ /g;s/2/▂/g;s/3/▃/g;s/4/▄/g;s/5/▅/g;s/6/▆/g;s/7/▇/g'