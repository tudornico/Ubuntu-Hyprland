#!/bin/bash
pkill -x cava
stdbuf -i0 -o0 -e0 cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-8]//g;s/8/█/g;s/7/▇/g;s/6/▆/g;s/5/▅/g;s/4/▄/g;s/3/▃/g;s/2/▂/g;s/1/ /g;s/0/ /g'