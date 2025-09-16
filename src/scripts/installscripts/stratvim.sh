#!/bin/env bash

echo [Installing Dependencies]
sudo pacman -S npm neovim xclip lazygit --noconfirm || exit 1

echo [Installing Neovim Configs] 
git clone https://github.com/StratOS-Linux/StratVIM.git ~/.config/nvim || exit 2

