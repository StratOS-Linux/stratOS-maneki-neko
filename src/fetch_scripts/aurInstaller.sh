#!/bin/bash

# Define your main function
manekiAURInstaller() {
    echo "Installing AUR programs.."
    # Your code here...

    for package in "$@"; do
        # Install the aur application 
        yay -S "$package"
    done
}


# Execute the main function with administrator privileges
pkexec bash -c "$(declare -f manekiAURInstaller); manekiAURInstaller"
