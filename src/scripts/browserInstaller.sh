#!/bin/bash
menu() {
    dialog --clear --backtitle "Browser Selector" \
        --title "Select a browser" \
        --menu "Choose one of the following options:" 15 40 3 \
        1 "Chromium" \
        2 "Brave" \
        3 "Librewolf" \
        2>&1 >/dev/tty
}

while true; do
    choice=$(menu)
    case $choice in
        1)
            echo "Setting default browser to Chromium"
	    yay -S chromium --noconfirm
	    xdg-settings set default-web-browser chromium.desktop
            ;;
        2)
            echo "Setting default browser to Brave"
	    yay -S brave-bin --noconfirm
	    xdg-settings set default-web-browser brave-browser.desktop
            ;;
        3)
            echo "Setting default browser to Librewolf"
	    yay -S librewolf-bin --noconfirm
	    xdg-settings set default-web-browser librewolf.desktop
            ;;
        *)
            echo "Exiting..."
            exit 0
            ;;
    esac
done
