#!/bin/bash


manekiPACMANInstaller() {
    echo "==> ==> ==> Installing Pacman programs ....Cc....o..."
    # Install all packages at once
    pacman -Syy --noconfirm "$@"
}

# Function to execute with elevated privileges
execute_with_privileges() {
    if command -v pkexec &> /dev/null; then
        if pkexec bash -c "$(declare -f manekiPACMANInstaller); manekiPACMANInstaller $*"; then
            return 0
        else
            echo "manekiPACMANInstaller():MESSAGE:: pkexec failed. Falling back to sudo."
        fi
    else
        echo "manekiPACMANInstaler():MESSAGE:: pkexec not found. Falling back to sudo."
    fi

    # Fallback to sudo
    if command -v sudo &> /dev/null; then
        sudo bash -c "$(declare -f manekiPACMANInstaller); manekiPACMANInstaller $*"
    else
        echo "manekiPACMANInstaller():FATAL:: Neither pkexec nor sudo is available. Cannot install programs."
        return 1
    fi
}

# Execute the function with elevated privileges
execute_with_privileges "$@"