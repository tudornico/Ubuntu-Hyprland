#!/bin/bash

pkill -x cava
sleep 0.5

# We use a mix of lower and upper block characters to create 14 distinct heights
stdbuf -oL cava -p ~/.config/cava/config_waybar | while read -r line; do
    echo "$line" | sed 's/14/█/g; s/13/▇/g; s/12/▆/g; s/11/▅/g; s/10/▄/g; s/9/▃/g; s/8/▂/g; s/7/ /g; s/6/ /g; s/5/ /g; s/4/ /g; s/3/ /g; s/2/ /g; s/1/ /g; s/0/ /g'
done