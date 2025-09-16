#!/bin/bash
# flatpakPackageInstaller.sh
# Usage: flatpakPackageInstaller.sh <pkg1> <pkg2> ...
# This script installs flatpak packages either system-wide (if root) or user-only (if non-root).
# Status codes: 0=success, -1=flatpak error, 1+=package index that failed

if [ "$#" -eq 0 ]; then
    echo "No packages specified. Usage: $0 <pkg1> <pkg2> ..." >&2
    exit -1
fi

# Check if flatpak is available
if ! command -v flatpak &> /dev/null; then
    echo "flatpak is not available. Please install flatpak first." >&2
    exit -1
fi

export TOTAL_PACKAGES=$#
export FAILED_PACKAGES=""
export SUCCESS_COUNT=0
export PACKAGES=("$@")

# Determine installation scope based on privileges
if [ "$EUID" -eq 0 ]; then
    INSTALL_SCOPE="--system"
    SCOPE_DESC="system-wide"
    echo "==> Running with root privileges - installing flatpaks system-wide..."
else
    INSTALL_SCOPE="--user"
    SCOPE_DESC="user-only"
    echo "==> Running as user - installing flatpaks for current user only..."
fi

echo "==> Starting flatpak package installation for $TOTAL_PACKAGES packages ($SCOPE_DESC)..."

# Test network connectivity by pinging flathub
if ! ping -c 1 -W 3 flathub.org &>/dev/null; then
    echo "[ERROR] No network connectivity detected. Please check your internet connection." >&2
    echo -e "Exit Code: -1"
    exit -1
fi



progress_char="*"
package_index=1

for pkg in "${PACKAGES[@]}"; do
    echo -e "\n==> Installing package $package_index/$TOTAL_PACKAGES: $pkg ($SCOPE_DESC)"
    
    # Install with flatpak using appropriate scope
    # Redirect output and show progress characters
    if flatpak install flathub $INSTALL_SCOPE --noninteractive --assumeyes "$pkg" 2>&1 | while IFS= read -r line; do
        printf "%s" "$progress_char"
        # Show important error messages
        if [[ "$line" == *"error"* || "$line" == *"failed"* || "$line" == *"not found"* || "$line" == *"Error"* ]]; then
            echo -e "\n$line" >&2
        fi
        # Show permission-related messages
        if [[ "$line" == *"permission"* || "$line" == *"denied"* ]]; then
            echo -e "\n$line" >&2
        fi
    done; then
        echo -e "\n[OK] $pkg installed successfully ($SCOPE_DESC)."
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "\n[ERROR] Failed to install $pkg ($SCOPE_DESC)" >&2
        FAILED_PACKAGES="${FAILED_PACKAGES}${package_index}"
    fi
    
    package_index=$((package_index + 1))
done

# Calculate exit code based on results
if [ -z "$FAILED_PACKAGES" ]; then
    echo -e "\n==> All $TOTAL_PACKAGES flatpak packages installed successfully ($SCOPE_DESC)!"
    echo -e "\n==> Exit code: 0"
    exit 0
elif [ $SUCCESS_COUNT -eq 0 ]; then
    echo -e "\n==> All packages failed to install."
    # Return first failed package index if all failed
    echo -e "\n==> Exit code: ${FAILED_PACKAGES:0:1}"
    exit ${FAILED_PACKAGES:0:1}
else
    echo -e "\n==> Partial success: $SUCCESS_COUNT/$TOTAL_PACKAGES packages installed ($SCOPE_DESC)."
    echo "==> Failed package indices: $FAILED_PACKAGES"
    # Construct exit code: failed_indices + 0 (e.g., 30, 240, etc.)
    exit_code="${FAILED_PACKAGES}0"
    echo -e "\n==> Exit code: $exit_code"
    exit $exit_code
fi