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

    # Check if 'MimeType' supports mp4, mp3, mkv, mov, aac, m4a formats
    if [[ $mime_type == *"video/mp4"* || $mime_type == *"audio/mpeg"* || $mime_type == *"video/x-matroska"* || $mime_type == *"video/quicktime"* || $mime_type == *"audio/aac"* || $mime_type == *"audio/x-m4a"* ]] && [[ $categories == *"AudioVideo"* || $categories == *"Player"* ]]; then
        echo "$name||$file"
        echo ";"
    fi
  done
else
  echo "Directory $dir does not exist."
fi
