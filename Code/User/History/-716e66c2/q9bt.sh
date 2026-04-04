#!/bin/bash
pkill -x cava
sleep 0.1

# We change '0' and '1' to a very small dot or thin line
# This prevents the "empty gap" look during quiet high-pitched parts
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-7]//g;s/0/ /g;s/1/./g;s/2/▂/g;s/3/▃/g;s/4/▄/g;s/5/▅/g;s/6/▆/g;s/7/▇/g'