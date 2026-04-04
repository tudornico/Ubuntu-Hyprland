# #!/bin/bash

# PULSE=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█" "▇" "▆" "▅" "▄" "▃" "▂")
# i=0

# while true; do
#     player=$(playerctl -l 2>/dev/null | while read p; do
#         [ "$(playerctl -p "$p" status 2>/dev/null)" = "Playing" ] && echo "$p" && break
#     done)

#     if [ -n "$player" ]; then
#         artist=$(playerctl -p "$player" metadata artist 2>/dev/null)
#         title=$(playerctl -p "$player" metadata title 2>/dev/null)
#         bar="${PULSE[$i]} ${PULSE[(i+2)%14]} ${PULSE[(i+5)%14]} ${PULSE[(i+8)%14]} ${PULSE[(i+11)%14]}"
#         echo "{\"text\": \"$bar  $title — $artist\", \"class\": \"playing\"}"
#         i=$(( (i+1) % 14 ))
#     else
#         echo "{\"text\": \"\", \"class\": \"stopped\"}"
#         i=0
#     fi
#     sleep 0.3
# done
