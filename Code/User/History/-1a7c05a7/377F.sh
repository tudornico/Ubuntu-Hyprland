#!/bin/bash

# Clean up cava on exit
trap "pkill cava" EXIT

# Run cava and pipe it to a loop that replaces numbers with bar characters
cava -p ~/.config/cava/config_waybar | sed -u 's/0/ /g; s/1/▂/g; s/2/▃/g; s/3/▄/g; s/4/▅/g; s/5/▆/g; s/6/▇/g; s/7/█/g;'