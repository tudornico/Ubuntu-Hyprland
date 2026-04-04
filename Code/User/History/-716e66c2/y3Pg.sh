#!/bin/bash
pkill -x cava
# The [^0-7] part deletes anything that isn't a number (the lag-maker)
stdbuf -oL cava -p ~/.config/cava/config_waybar | sed -u 's/[^0-7]//g;s/0/ /g;s/1/▂/g;s/2/▃/g;s/3/▄/g;s/4/▅/g;s/5/▆/g;s/6/▇/g;s/7/█/g'