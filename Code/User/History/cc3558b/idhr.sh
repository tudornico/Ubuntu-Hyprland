cat > ~/.config/waybar/mediaplayer.sh << 'EOF'
#!/bin/bash

BLOCKS=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")

while true; do
    while IFS= read -r line; do
        # Skip non-numeric lines from cava
        [[ "$line" =~ ^[0-9\ ]+$ ]] || continue

        player=$(playerctl -l 2>/dev/null | while read p; do
            [ "$(playerctl -p "$p" status 2>/dev/null)" = "Playing" ] && echo "$p" && break
        done)

        if [ -n "$player" ]; then
            artist=$(playerctl -p "$player" metadata artist 2>/dev/null | sed 's/&/\&amp;/g')
            title=$(playerctl -p "$player" metadata title 2>/dev/null | sed 's/&/\&amp;/g')

            bar=""
            for val in $line; do
                bar+="${BLOCKS[$((val > 7 ? 7 : val))]}"
            done

            echo "{\"text\": \"${bar}  ${title} — ${artist}\", \"class\": \"playing\"}" || break
        else
            echo "{\"text\": \"\", \"class\": \"stopped\"}" || break
        fi
    done < <(cava -p ~/.config/cava/waybar-config 2>/dev/null)
    sleep 1
done
EOF
chmod +x ~/.config/waybar/mediaplayer.sh