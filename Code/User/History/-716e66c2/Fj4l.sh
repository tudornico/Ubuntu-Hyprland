#!/bin/bash

# Clean up cava on exit
trap "pkill -P $$" EXIT

# We add 'stdbuf -oL' to ensure the output isn't buffered
stdbuf -oL cava -p ~/.config/cava/config_waybar | sed -u 's/0/ /g; s/1/▂/g; s/2/▃/g; s/3/▄/g; s/4/▅/g; s/5/▆/g; s/6/▇/g; s/7/█/g;'