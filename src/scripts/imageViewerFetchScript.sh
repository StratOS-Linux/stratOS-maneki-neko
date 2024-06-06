#!/bin/bash


printImageViewers(){
  # Directory containing .desktop files

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

      # Check if 'MimeType' supports image formats and if it's a viewer or a web browser
      if [[ $mime_type == *"image/"* ]] && [[ $categories == *"Graphics"* ]]; then
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
printImageViewers "$HOME/.local/share/flatpak/exports/share/applications/"
printImageViewers "/usr/share/applications/"
printImageViewers "/var/lib/flatpak/exports/share/applications/"