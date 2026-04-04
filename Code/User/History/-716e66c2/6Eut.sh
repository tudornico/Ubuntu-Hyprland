#!/bin/bash
pkill -x cava
sleep 0.1

# 1. We added 's/8/█/g' and 's/7/▇/g' for the extra height
# 2. Kept it unbuffered (-u) to prevent the lag we fixed earlier
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-8]//g;s/8/█/g;s/7/▇/g;s/6/▆/g;s/5/▅/g;s/4/▄/g;s/3/▃/g;s/2/▂/g;s/1/ /g;s/0/ /g'