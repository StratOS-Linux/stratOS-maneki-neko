#!/bin/bash

printWebBrowsers() {
  # directory containing .desktop files
  local dir=$1

  # Check if directory exists
  if [ -d "$dir" ]; then
    # Find .desktop files
    local files=$(find "$dir" -name "*.desktop")

    # Check each .desktop file
    for file in $files; do
      # Extract 'Name', 'MimeType', 'Categories', and 'Keywords' parameters
      local name=$(awk -F= '/\[Desktop Entry\]/,/Name=/ { if ($1 == "Name") print $2 }' "$file")
      local mime_type=$(grep -E '^MimeType=' "$file" | cut -d'=' -f2)
      local categories=$(grep -E '^Categories=' "$file" | cut -d'=' -f2)

      # Check if 'MimeType' supports http/https and 'Categories' contain 'Network' and 'WebBrowser'
      if [[ $mime_type == *"x-scheme-handler/http"* || $mime_type == *"x-scheme-handler/https"* ]] && [[ $categories == *"Network"* && $categories == *"WebBrowser"* ]]; then
          echo "$name||$file"
          echo ";"
      fi
    done
  else
      # if directory not found then print nothing and exit function

    : 
  fi
}

# Call the function with the provided directories
printWebBrowsers "$HOME/.local/share/flatpak/exports/share/applications/"
printWebBrowsers "/usr/share/applications/"
printWebBrowsers "/var/lib/flatpak/exports/share/applications/"

echo EOS