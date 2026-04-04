#!/bin/bash
pkill -x cava
# Using 'tr' is the most performant way to swap characters in a stream
stdbuf -oL cava -p ~/.config/cava/config_waybar | stdbuf -oL tr '01234567;' ' ▂▃▄▅▆▇█ '