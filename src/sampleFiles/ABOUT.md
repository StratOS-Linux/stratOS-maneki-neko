
# Sample Files Folder

This folder contains sample files that Maneki Neko will use with `mimeopen` command to set the default application to open a specific file on the preferred application.

## How it works?

1. From maneki, the user pressed button to change the default PDF viewer.
2. The command `mimeopen -d ../src/samplefiles/samplePDF.pdf` would be executed on another terminal window.
3. The command will automatically fetch the installed programs that can open a PDF document.
4. The user should then choose the preferred application from the terminal window by entering the appropriate button.
