#!/usr/bin/env bash
set -euo pipefail

# Function to output error message
handle_error() {
  local exit_code=$1
  local msg=$2
  echo "[Error: $msg]"
  exit "$exit_code"
}

# Check if running on StratOS Linux
if ! grep -q "StratOS" /etc/os-release; then
  handle_error 1 "This script is intended to run only on StratOS Linux"
fi

# Output to indicate dependenciesbeing installed
echo "[Installing Dependencies]"

# Install necessary packages using pacman. Exit with code 1 if the command fails.
sudo pacman -S npm neovim xclip lazygit --noconfirm || handle_error 1 "Failed to install dependencies"

# Output to indicate Neovim configuration is being cloned
echo "[Installing Neovim Configs]"

# Clone the StratVIM Git repository into the Neovim configuration directory. Exit with code 2 if the command fails.
if [ -d "~/.config/nvim" ]; then
  echo "[Warning: ~/.config/nvim already exists, deleting it to proceed with the installation]"
  rm -rf ~/.config/nvim
fi

git clone https://github.com/StratOS-Linux/StratVIM.git ~/.config/nvim || handle_error 2 "Failed to clone StratVIM repository"

# Exit with code 0 to indicate success
echo "[Installation successful]"
exit 0