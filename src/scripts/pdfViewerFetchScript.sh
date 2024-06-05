#!/bin/bash

# Directory containing .desktop files
dir="/usr/share/applications"

# Check if directory exists
if [ -d "$dir" ]; then
  # Find .desktop files
  files=$(find "$dir" -name "*.desktop")

  # Check each .desktop file
  for file in $files; do
    # Extract 'Name', 'MimeType', 'Categories', and 'Keywords' parameters
    name=$(awk -F= '/\[Desktop Entry\]/,/Name=/ { if ($1 == "Name") {print $2; exit} }' "$file")
    mime_type=$(grep -E '^MimeType=' "$file" | cut -d'=' -f2)
    categories=$(grep -E '^Categories=' "$file" | cut -d'=' -f2)

    # Check if 'MimeType' supports pdf format
    if [[ $mime_type == *"application/pdf"* || $mime_type == *"x-scheme-handler/http"* || $mime_type == *"x-scheme-handler/https"* ]] \
    && [[ $categories == *"Viewer"* || $categories == *"DocumentViewer"* || $categories == *"WebBrowser"* ]]; then
        echo "$name||$file"
        echo ";"
    fi
  done
else
  echo "Directory $dir does not exist."
fi
