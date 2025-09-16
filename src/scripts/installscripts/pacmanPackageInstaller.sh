#!/bin/bash
# pacmanPackageInstaller.sh
# Usage: pkexec pacmanPackageInstaller.sh [-y|--yankrepos] <pkg1> <pkg2> ...
# This script installs pacman packages and should be executed as root via pkexec.
# Flags: -y or --yankrepos to sync package databases before installing
# Status codes: 0=success, -1=pacman error, 1+=package index that failed

# Parse flags
SYNC_REPOS=false
PACKAGES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yankrepos)
            SYNC_REPOS=true
            shift
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

# Check if running as root (required for pacman operations)
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Use: pkexec $0 <packages>" >&2
    exit -1
fi

# Check if pacman is available
if ! command -v pacman &> /dev/null; then
    echo "pacman is not available. This script requires Arch Linux or pacman-based system." >&2
    exit -1
fi

if [ "${#PACKAGES[@]}" -eq 0 ]; then
    echo "No packages specified. Usage: pkexec $0 [-y|--yankrepos] <pkg1> <pkg2> ..." >&2
    exit -1
fi

export TOTAL_PACKAGES=${#PACKAGES[@]}
export FAILED_PACKAGES=""
export SUCCESS_COUNT=0

echo "==> Starting pacman package installation for $TOTAL_PACKAGES packages..."
echo "==> Running with root privileges..."

# Test network connectivity by pinging Arch Linux mirror
if ! ping -c 1 -W 3 archlinux.org &>/dev/null; then
    echo "[ERROR] No network connectivity detected. Please check your internet connection." >&2
    echo -e "Exit Code: -1"
    exit -1
fi

# Sync package databases if flag is provided
if [ "$SYNC_REPOS" = true ]; then
    echo "==> Syncing package databases..."
    if ! pacman -Sy &>/dev/null; then
        echo "[ERROR] Failed to sync package databases. Check pacman status." >&2
        echo -e "Exit Code: -1"
        exit -1
    fi
fi

progress_char="*"
package_index=1

for pkg in "${PACKAGES[@]}"; do
    echo -e "\n==> Installing package $package_index/$TOTAL_PACKAGES: $pkg"
    
    # Install with pacman directly (already running as root via pkexec)
    # Redirect output and show progress characters
    if pacman -S --noconfirm --needed "$pkg" 2>&1 | while IFS= read -r line; do
        printf "%s" "$progress_char"
        # Show important error messages
        if [[ "$line" == *"error"* || "$line" == *"failed"* || "$line" == *"not found"* ]]; then
            echo -e "\n$line" >&2
        fi
    done; then
        echo -e "\n[OK] $pkg installed successfully."
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "\n[ERROR] Failed to install $pkg" >&2
        FAILED_PACKAGES="${FAILED_PACKAGES}${package_index}"
    fi
    
    package_index=$((package_index + 1))
done

# Calculate exit code based on results
if [ -z "$FAILED_PACKAGES" ]; then
    echo -e "\n==> All $TOTAL_PACKAGES pacman packages installed successfully!"
    echo -e "\n==> Exit code: 0"
    exit 0
elif [ $SUCCESS_COUNT -eq 0 ]; then
    echo -e "\n==> All packages failed to install."
    # Return first failed package index if all failed
    echo -e "\n==> Exit code: ${FAILED_PACKAGES:0:1}"
    exit ${FAILED_PACKAGES:0:1}
else
    echo -e "\n==> Partial success: $SUCCESS_COUNT/$TOTAL_PACKAGES packages installed."
    echo "==> Failed package indices: $FAILED_PACKAGES"
    # Construct exit code: failed_indices + 0 (e.g., 30, 240, etc.)
    exit_code="${FAILED_PACKAGES}0"
    echo -e "\n==> Exit code: $exit_code"
    exit $exit_code
fi