#!/usr/bin/bash

# ASCII art
echo "
⠀⠀⠀⣀⣄⣀⠀⠀⠀⠀⠀⠀⣀⣠⣀⠀⠀⠀⠀⠀
⠀⠀⢸⣿⣩⣿⣷⣶⣶⣶⣶⣾⣿⣍⣿⡇⠀⠀⠀⠀
⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣀⣀⡀⠀
⠀⠀⣾⣿⠟⠉⠉⠻⣿⣿⠟⠉⠉⠛⠀⣿⣿⣿⣿⣦
⠀⢠⣿⣿⣷⡿⢿⣾⠛⠛⣷⡿⣿⣾⣦⣈⠉⠙⠛⠋
⠀⠀⢿⣿⣿⣧⣤⣀⣤⣤⣀⣤⣼⣿⣿⡿⠀⣼⡿⠀
⠀⣀⣬⠻⠿⢿⣿⣿⣿⣿⣿⣿⡿⠿⠟⣁⠐⡿⠃⠀
⣸⣿⣿⠀⠀⠀⠀⠀⢠⡄⠀⠀⢀⣀⣼⣿⡆⠀⠀⠀
⣿⣿⣿⣷⣶⣄⠙⣧⣄⣠⣼⣿⣿⣿⣿⣿⣷⠀⠀⠀
⠘⢿⣿⣿⣿⣿⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⣤⣄⡉⠙⠋⣁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀
⠟⠉⣉⣉⡉⠙⠿⣿⣿⣿⣿⠿⠋⢉⣉⣉⠉⠻⠀⠀
⢠⣾⣿⣿⣿⣷⣦⡈⢻⡟⢁⣴⣾⣿⣿⣿⣷⡄⠀⠀
⠸⣿⣿⣿⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⣿⣿⣿⠇⠀⠀
⠀⠈⠉⠙⠛⠉⠉⠀⠀⠀⠀⠉⠉⠛⠋⠉⠁⠀⠀⠀
"

echo "==== ==== >> Set the Default PDF Application << ==== ===="
echo

# Function to display dialog
show_dialog() {
    dialog --msgbox "$1" 8 40
    clear
}

# Function to set default application and show dialog
set_default_and_show_dialog() {
    if mimeopen -d $(pwd)/src/scripts/mimeopenScripts/sampleFiles/sample.pdf 2>/dev/null ; then
        echo "==> ==> Selected application will be launched now..."
        show_dialog "The Default PDF App has been set."
    else
        echo "==> ==> Process interrupted or failed."
    fi
}

# Trap Ctrl+C and terminal close
trap "echo -e '\n==> ==> Process interrupted.'; exit 1" INT TERM

# Run the function in a subshell to handle potential interrupts
(set_default_and_show_dialog)

# If the subshell was interrupted, this part won't execute
exit 0