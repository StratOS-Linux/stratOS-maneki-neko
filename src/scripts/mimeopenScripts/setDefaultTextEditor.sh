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
echo "==== ==== >> Set the Default Text Editor Application << ==== ===="
echo

# Function to display dialog
show_dialog() {
    dialog --msgbox "$1" 8 40
    clear
}

# Function to set default application and show dialog
set_default_and_show_dialog() {

    # create (temporary) empty .C, .JAVA, .YAML, .TOML, .SH, .P6, .TEX, .JS, .PS1, .RS, .CONF, .BASHRC, .ZSHRC files in /tmp directory
    touch /tmp/sample.c /tmp/sample.java
    touch /tmp/sample.yaml /tmp/sample.toml
    touch /tmp/sample.sh /tmp/sample.p6
    touch /tmp/sample.tex /tmp/sample.js
    touch /tmp/sample.ps1 /tmp/sample.rs
    touch /tmp/sample.conf /tmp/.bashrc /tmp/.zshrc

    if mimeopen -d $(pwd)/src/scripts/mimeopenScripts/sampleFiles/sample.py $(pwd)/src/scripts/mimeopenScripts/sampleFiles/sample.cpp  /tmp/sample.c /tmp/sample.java /tmp/sample.yaml /tmp/sample.toml /tmp/sample.sh /tmp/sample.p6 /tmp/sample.tex /tmp/sample.js /tmp/sample.ps1 /tmp/sample.rs /tmp/sample.conf /tmp/.bashrc /tmp/.zshrc $(pwd)/src/scripts/mimeopenScripts/sampleFiles/sample.txt 2>/dev/null; then
        echo "==> ==> Selected application will be launched now..."
        show_dialog "The Default Text Editor App has been set."
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