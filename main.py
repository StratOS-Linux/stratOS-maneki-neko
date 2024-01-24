#!/usr/bin/env python
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui

from PyQt5.QtWidgets import QMainWindow,  QApplication,  QDialog

from time import sleep

import os, subprocess

# globals
app = QApplication(sys.argv)
totalPages=3


class welcomeScreen(QMainWindow):

    def __init__(self):
        # init the class
        super(welcomeScreen,self).__init__()
        # load the ui file
        loadUi("src/ui/TokyoNight-Dark/welcomeScreen.ui",self)

        # always init window to first page
        self.windowStackedWidget.setCurrentIndex(0)
        # if AUTOSTART already enabled, then update the text of the autostartCheckBox
        self.updateAutostartCheckBoxState()
        # Buttons
        self.nextButton.clicked.connect(self.moveForward)
        self.backButton.clicked.connect(self.moveBackward)
        self.distroInstallerButton.clicked.connect(self.runDistroInstallerScript)
        self.changeThemeButton.clicked.connect(self.runThemeChangerScript)
        self.browserInstallerButton.clicked.connect(self.runBrowserInstallerScript)
        self.openLUGVITCbutton.clicked.connect(self.openLUGVITC_Website)
        self.openFORUMbutton.clicked.connect(self.openFORUM_Website)
        self.autostartCheckBox.clicked.connect(self.setupAutostart)
        self.creditsButton.clicked.connect(self.openCreditsDialog)


        return

    def updateAutostartCheckBoxState(self):
        # purpose of this function is to update the text of 
        # autostart checkbox to Enabled if the desktop file already exists
        home = os.path.expanduser("~")
        filePath = home + "/.config/autostart/maneki_neko.desktop"
        print(filePath)

        if os.path.isfile(filePath):
            # the file exists so update the checkbox text
            self.autostartCheckBox.setText("Autostart Maneki Neko (Enabled)")
            self.autostartCheckBox.setChecked(True)

        return

    def disableBackAtFirstPage(self):
        currentIndex = self.windowStackedWidget.currentIndex() #current index of the window
        # disable back button if at first page
        if currentIndex == 0:
            self.backButton.setEnabled(False)
            return

    def moveForward(self):
        global totalPages
        currentIndex = self.windowStackedWidget.currentIndex() #current index of the window
        
        # if already in last page then exit
        if currentIndex+1 == totalPages:
            print("Exiting...")
            app.exec_()
            exit()

        # change page by one forward
        self.windowStackedWidget.setCurrentIndex(currentIndex+1)

        # now enable back button
        self.backButton.setEnabled(True)


        # morph the button to "Exit" button on last page
        currentIndex = self.windowStackedWidget.currentIndex() #updated index of the window
        if currentIndex+1 == totalPages:
            self.morphNextButton()
        return

    def moveBackward(self):
        currentIndex = self.windowStackedWidget.currentIndex()

        # go back until currentIndex is 0
        if currentIndex >= 0:
            self.windowStackedWidget.setCurrentIndex(currentIndex-1)
        
        # call func to disable back button at first page
        self.disableBackAtFirstPage()

        # to undo morph (from "Exit" to "Next")
        self.morphNextButton()

        return
    
    def morphNextButton(self):
        currentIndex = self.windowStackedWidget.currentIndex()

        # set button label to "Next" as long as it is not on last page
        if currentIndex+1 != totalPages: 
            self.nextButton.setText("Next")
        else:
            self.nextButton.setText("Exit")

    def runDistroInstallerScript(self):

        # work need to be done
        print("executing the installer script")

        # the command to execute
        # pls change this
        command = ["gnome-terminal", "--", 'bash -c /home/kali/Desktop/stratOS_welcome/src/scripts/distroInstaller.sh']

        temporary = subprocess.Popen(command,stdout=subprocess.PIPE)

        # get the STDOUT
        result=temporary.communicate()

        #print(result)

        return

    def runThemeChangerScript(self):
        # work need to be done
        print("executing the installer script")

        # the command to execute
        # pls change this
        command = ["gnome-terminal", "--", 'bash -c /home/kali/Desktop/stratOS_welcome/src/scripts/themeChanger.sh']

        temporary = subprocess.Popen(command,stdout=subprocess.PIPE)

        # get the STDOUT
        result=temporary.communicate()

        #print(result)

        return

    def runBrowserInstallerScript(self):
        # work need to be done
        print("executing the installer script")

        # the command to execute
        # pls change this

        command = ["gnome-terminal", "--", '$HOME/Desktop/stratOS_welcome/src/scripts/browserInstaller.sh']

        temporary = subprocess.Popen(command,stdout=subprocess.PIPE)

        # get the STDOUT
        result=temporary.communicate()

        #print(result)

        return

    def openLUGVITC_Website(self):
        # command to open the URL
        command = ["xdg-open", "www.lugvitc.org"]
        run = subprocess.Popen(command)
        print("Opening LUGVITC website on default browser")
        return
    
    def openFORUM_Website(self):
        # command to open the URL
        command = ["xdg-open", "https://forum.lugvitc.org"]
        run = subprocess.Popen(command)
        print("Opening LUGVITC forum website on default browser")

        return

    def openCreditsDialog(self):
        dialog = creditsWindow()
        if dialog.exec_():
            return

    def setupAutostart(self):
        # define home and the full file path
        home = os.path.expanduser("~")
        filePath = home + "/.config/autostart/maneki_neko.desktop" # full path to desktop file
        

        # create the desktop file and save it in $HOME/.config/autostart when the checkBox is checked
        if self.autostartCheckBox.isChecked():
            pwd = os.getcwd()
            # returns this running script's file name
            thisScriptFileName = os.path.basename(__file__)

            # opening the file in write mode
            with open(filePath,"w") as f:

                fileContent=f"""
[Desktop Entry]
Type=Application
Name=Maneki Neko
Exec=python3 {pwd}/{thisScriptFileName}
Icon={pwd}/src/png/logo.png
Comment=stratOS welcome screen
X-GNOME-Autostart-enabled=true
Path={pwd}
Terminal=false
StartupNotify=false
                    """
                f.write(fileContent)
                # end of with block
            print("setupAutostart():create desktop file:OK")

            #make file executable
            command = ["chmod", "+x", filePath] 
            run = subprocess.Popen(command)
            print("setupAutostart():make desktop file executable:OK")

            print("Maneki Neko autostart Enabled")

            # update checkbox text for feedback
            self.autostartCheckBox.setText("Autostart Maneki Neko (Enabled)")

        else:
            try:
                os.remove(filePath)
                # update checkbox text for feedback
                self.autostartCheckBox.setText("Autostart Maneki Neko (Disabled)")
                print("Maneki Neko autostart Disabled")


            except Exception as E:
                print("setupAutostart():remove: desktop file was not found anyway")
                self.autostartCheckBox.setText("Autostart Maneki Neko")

        return


def main():
    global app
    print("Program launch OK")
    mainScreen = welcomeScreen()
    mainScreen.setWindowIcon(QtGui.QIcon("src/png/maneki_neko.png"))
    mainScreen.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting...")
    
    return



class creditsWindow(QDialog):
    def __init__(self):
        # init the class and the ui file
        super(creditsWindow,self).__init__()
        loadUi("src/ui/creditsDialog.ui",self)

        self.openBedrockSiteButton.clicked.connect(self.openBedrockWebsite)
        self.openGithubRepo.clicked.connect(self.openLUGVITCrepo)

        return
    
    def openBedrockWebsite(self):
        # the command to open the website
        command = ['xdg-open', 'https://bedrocklinux.org/']

        # run the command
        run = subprocess.Popen(command)
        print("Opening Bedrock Linux website on default browser.")
        return

    def openLUGVITCrepo(self):
        # the command to open the website
        command = ['xdg-open', 'https://github.com/lugvitc']

        # run the command
        run = subprocess.Popen(command)
        print("Opening LUGVITC Github repo on default browser.")
        return




if __name__ == "__main__":
    main()
