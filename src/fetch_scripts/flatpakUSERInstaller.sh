#!/bin/bash



for package in "$@"; do
    # Install the flatpak application 
    flatpak install --user "$package" | echo
done




