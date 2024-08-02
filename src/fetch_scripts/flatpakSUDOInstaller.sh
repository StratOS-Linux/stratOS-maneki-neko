#!/bin/bash

# Define your main function
manekiFLATPAKInstaller() {
    echo "Installing flatpaks"
    # Your code here...

    for package in "$@"; do
        output=$(flatpak install --system "$package" 2>&1)

        # Check if the installation was successful
        if [[ $? -eq 0 ]]; then
            echo "Package installed successfully!"
        else
            echo "Error installing package. Details:"
            echo "$output"
            break
        fi
    done
}

# Execute the entire script with administrator privileges
pkexec bash -c "$(declare -f manekiFLATPAKInstaller); manekiFLATPAKInstaller"

