
# Sample Files Folder

This folder contains sample files that Maneki Neko will use with `mimeopen` command to set the default application to open a specific file on the preferred application.

## How it works?

1. From maneki, the user pressed button to change the default PDF viewer.
2. The command `mimeopen -d ../src/samplefiles/samplePDF.pdf` would be executed on another terminal window.
3. The command will automatically fetch the installed programs that can open a PDF document.
4. The user should then choose the preferred application from the terminal window by entering the appropriate button.


## Command to set default word processor
`mimeopen -d ./sample.odt ./sample.doc ./sample.docx`

## Command to set default text editor
`mimeopen -d ./sample.py ./sample.text ./sample.cpp ./sample.c ./sample.md ./sample.java ./sample.yaml ./sample.toml ./sample.sh ./sample.p6 ./sample.tex ./sample.js`

## Command to set default PDF viewer
`mimeopen

