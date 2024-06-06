#!/usr/bin/env python

import subprocess, os


def fetchScripts(WORK_DIR):

    # script to run all fetch scripts
    installedWebBrowsers    = {}
    installedImageViewers   = {}
    installedMediaPlayers   = {}
    installedPDFViewers     = {}
    installedTextEditors    = {}
    installedDOCXEditors    = {}
    installedPPTXEditors    = {}
    installedXLSXEditors    = {}

    listOfScripts = ["browserFetchScript.sh", "imageViewerFetchScript.sh", \
        "mediaPlayerFetchScript.sh", "pdfViewerFetchScript.sh", "textEditorFetchScript.sh"]
    
    for eachScript in listOfScripts:
        command = ["bash", "-c", WORK_DIR + "/src/fetch_scripts/" + eachScript]
        temporary = subprocess.Popen(command,stdout=subprocess.PIPE)
        output = [x.split("||") for x in str(temporary.communicate()[0].decode("UTF-8")).split(";\n")[::-1]][1::]

        for i in range(len(output)):
            if output[i][0] == "":
                output[i][0] = output[i][1].split("/")[-1]
        
       

        print(output)
        print("\n\n")


    


WORK_DIR = os.getcwd()
fetchScripts(WORK_DIR)