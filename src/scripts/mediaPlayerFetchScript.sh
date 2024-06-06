#!/bin/bash


printMediaPlayers(){
  # Directory containing .desktop files

  local dir=$1
# Check if directory exists

  if [ -d "$dir" ]; then
    # Find .desktop files
    local files=$(find "$dir" -name "*.desktop")

    # Check each .desktop file
    for file in $files; do
    # Extract 'Name', 'MimeType', 'Categories', and 'Keywords' parameters
      local name=$(awk -F= '/\[Desktop Entry\]/,/Name=/ { if ($1 == "Name") {print $2; exit} }' "$file")
      local mime_type=$(grep -E '^MimeType=' "$file" | cut -d'=' -f2)
      local categories=$(grep -E '^Categories=' "$file" | cut -d'=' -f2)

      # Check if 'MimeType' supports mp4, mp3, mkv, mov, aac, m4a formats
      if [[ $mime_type == *"video/mp4"* && $mime_type == *"audio/mpeg"* || $mime_type == *"video/x-matroska"* || $mime_type == *"video/quicktime"* && $mime_type == *"audio/aac"* && $mime_type == *"audio/x-m4a"* ]] && [[ $categories == *"AudioVideo"* || $categories == *"Player"* ]]; then
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
printMediaPlayers "$HOME/.local/share/flatpak/exports/share/applications/"
printMediaPlayers "/usr/share/applications/"
printMediaPlayers "/var/lib/flatpak/exports/share/applications/"

echo EOS