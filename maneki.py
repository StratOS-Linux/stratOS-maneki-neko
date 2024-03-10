#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,  QApplication,  QDialog, QMessageBox
from time import sleep
import os, subprocess

lastPage = 3
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
app = QApplication(sys.argv)

def runInTerm(cmd:str,mesg:str):
    if mesg: print(mesg)
    result = subprocess.Popen(["kgx", "--", cmd], stdout=subprocess.PIPE)
    out = result.communicate()
    return

def main():
    global app
    
    mainScreen = welcomeScreen()
    print("Program launch OK")
    mainScreen.setWindowIcon(QtGui.QIcon(f"{WORK_DIR}/src/png/maneki_neko.png"))
    mainScreen.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting...")
    return

class welcomeScreen(QMainWindow):
    defBrowsers = ['librewolf']
    defPlayers = []
    defOffice = []
    defEditors = []
    defMisc = []
    defApps = defBrowsers + defPlayers + defOffice + defEditors + defMisc

    def __init__(self):
        super(welcomeScreen, self).__init__()
        loadUi(f"{WORK_DIR}/src/ui/welcomeScreen.ui", self)
        self.windowStackedWidget.setCurrentIndex(0)
        # if AUTOSTART already enabled, then update the text of the autostartCheckBox
        self.updateAutostartCheckBoxState()
        
        # Buttons
        self.nextButton.clicked.connect(self.moveForward)   # also self.proceedToInstall
        self.backButton.clicked.connect(self.moveBackward)  
        self.distroInstallerButton.clicked.connect(self.runDistroInstaller)
        self.openDISCORDbutton.clicked.connect(self.openDiscord)
        self.openMASTODONbutton.clicked.connect(self.openMastodon)
        self.openMATRIXbutton.clicked.connect(self.openMatrix)
        self.autostartCheckBox.clicked.connect(self.setupAutostart)
        self.creditsButton.clicked.connect(self.openCredits)

        self.packageInstallerButton.clicked.connect(self.openPackageInstallerPage)
        self.MISClistWidget.itemClicked.connect(self.setMiscDesc)
        self.WEBlistWidget.itemClicked.connect(self.setWebDesc)
        self.TXTlistWidget.itemClicked.connect(self.setTxtDesc)
        self.MEDIAlistWidget.itemClicked.connect(self.setMediaDesc)
        self.OFFICElistWidget.itemClicked.connect(self.setOfficeDesc)
        self.selectDefaultApps()
        return
    
    def selectDefaultApps(self):
        for i in range(0,self.WEBlistWidget.count()):
            item = self.WEBlistWidget.item(i)
            if item.text().lower()in self.defBrowsers:
                item.setCheckState(QtCore.Qt.Checked)
  
        for i in range(0,self.MEDIAlistWidget.count()):
            item = self.MEDIAlistWidget.item(i)
            if item.text().lower()in self.defPlayers:
                item.setCheckState(QtCore.Qt.Checked)

        for i in range(0,self.OFFICElistWidget.count()):
            item = self.OFFICElistWidget.item(i)
            if item.text().lower()in self.defOffice:
                item.setCheckState(QtCore.Qt.Checked)
  
        for i in range(0,self.TXTlistWidget.count()):
            item = self.TXTlistWidget.item(i)
            if item.text().lower().split()[0] in self.defEditors:
                item.setCheckState(QtCore.Qt.Checked)

        for i in range(0,self.MISClistWidget.count()):
            item = self.MISClistWidget.item(i)
            if item.text().lower().split()[0] in self.defMisc:
                item.setCheckState(QtCore.Qt.Checked)
        return
    

    def openPackageInstallerPage(self):
        currentIndex = self.windowStackedWidget.currentIndex()
        self.windowStackedWidget.setCurrentIndex(currentIndex+1)
        self.morphNextButton()
        return

    def setMiscDesc(self):
        # function that shows details of selected package on description widget of MISC category
        refDict = { "atril"     : 11,    
                    "evince"    : 12,    
                    "github"    : 13,    
                    "obsidian"  : 14,    
                    "gsconnect" : 15
                }
        try:
            selectedApp = self.MISClistWidget.currentItem().text().lower().split()[0]
        # EXPLANATION: suppose I selected "Atril PDF Document Viewer"
        # 1. self.MISClistWidget.currentItem().text() = "Atril PDF Document Viewer"
        # 2. self.MISClistWidget.currentItem().text().lower() = "atril pdf document viewer"
        # 3. self.MISClistWidget.currentItem().text().lower().split() = ["atril", "pdf","document", "viewer"]
        # 4. self.MISClistWidget.currentItem().text().lower().split()[0] = "atril"
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return
    def setWebDesc(self):
        refDict = { "firefox"     : 0,    
                    "chromium"    : 1,    
                    "librewolf"   : 2,    
                    "brave"       : 3
                }
        try:
            selectedApp = self.WEBlistWidget.currentItem().text().lower()
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return
    
    def setTxtDesc(self):
        refDict = { "stratmacs"   : 8, 
                    "stratvim"    : 9,
                    "vscodium"    : 10
                }
        try:
            selectedApp = self.TXTlistWidget.currentItem().text().lower().split()[0]
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return
    
    def setMediaDesc(self):
        refDict = { "vlc"   : 4,
                    "mpv"   : 5
                }
        try:
            selectedApp = self.MEDIAlistWidget.currentItem().text().lower()
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return
    
    def setOfficeDesc(self):
        refDict = { "onlyoffice"    : 6,
                    "libreoffice"   : 7
                }
        try:
            selectedApp = self.OFFICElistWidget.currentItem().text().lower()
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return
    
    def updateAutostartCheckBoxState(self):
        filePath = f"{HOME}/.config/autostart/maneki_neko.desktop"
        # print("updateAutostartCheckBoxState(): file path to autostart directory:",filePath)

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


    def proceedToInstall(self):
        global names
        names = [
                    #   [pacman,flatpak,aur]
                [None, "com.vscodium.codium", "vscodium-bin"],
                ["atril", None, None],
                ["evince", None, None],
                [None, None, "github-desktop-bin"],
                ["obsidian", "md.obsidian.Obsidian", "obsidian-bin"],
                [None, None, "gsconnect-git"],
                ["libreoffice-fresh", "org.libreoffice.LibreOffice", None],
                ["stratmacs", None, None],
                ["stratvim", None, None],
                [None, "com.brave.Browser", "brave-bin"],
        ]

        # get the list of selected apps
        selectedApps = []
        for category in [self.WEBlistWidget, self.MEDIAlistWidget, self.OFFICElistWidget, self.TXTlistWidget, self.MISClistWidget]:
            for i in range(category.count()):
                item = category.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    selectedApps.append(item.text().lower().split()[0])

        # use names as reference to get the index of the selected apps. If index = 0, create an install string for pacman, 1 means flatpak, 2 means aur
        global programInstallQueue
        programInstallQueue = []
        for app in selectedApps:
            for i in range(len(names)):
                if app in names[i]:
                    programInstallQueue.insert([app, i])
                    break
        print("Selected apps:",selectedApps)
        print("Program install queue:",programInstallQueue)



    def moveForward(self):
        global lastPage
        currentIndex = self.windowStackedWidget.currentIndex() #current index of the window
        
        # if already in last page then exit
        if currentIndex+1 == lastPage:
            print("Exiting...")
            app.exec_()
            exit()
        
        # if at the 4th page ie. program installer button
        # the 'next' button gets morphed to 'install' button
        # adding the install functionality for the button at the 4th page only
        elif currentIndex+1 == 4:
            self.proceedToInstall()
            return

        # change page by one forward
        self.windowStackedWidget.setCurrentIndex(currentIndex+1)

        # now enable back button
        self.backButton.setEnabled(True)


        # morph the button to "Exit" button on last page
        currentIndex = self.windowStackedWidget.currentIndex() #updated index of the window
        if currentIndex+1 == lastPage:
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
        # if at 1st, 2nd page, button says "Next"
        if currentIndex+1 < lastPage: 
            self.nextButton.setText("Next")
        
        # if at the Package installer page, morph button to "Install"
        elif currentIndex+1 == 4:
            self.nextButton.setText("Install")
        # if button at 3rd page, it says "exit"
        else:
            self.nextButton.setText("Exit")


    def runDistroInstaller(self):
        runInTerm(f"bash /usr/local/bin/StratOS-configure-distro", "Running distro installer")
        return
    def runThemeChanger(self):
        runInTerm(f"bash /usr/local/bin/StratOS-configure-theme", "Running theme changer!")
        return
    def runBrowserInstaller(self):
        runInTerm(f"bash /usr/local/bin/StratOS-configure-browser", "Running browser installer")
        return
    def openWebsite(self):
        runInTerm(f"xdg-open https://stratos-linux.github.io", "Opening website")
        return
    def openMastodon(self):
        runInTerm(f"xdg-open https://fosstodon.org/@stratoslinux", "Opening Mastodon")
        return
    def openDiscord(self):
        runInTerm(f"xdg-open https://discord.gg/8sysF4ex", "Opening Discord")
        return
    def openMatrix(self):
        runInTerm(f"xdg-open https://matrix.to/#/#stratos-linux:matrix.org", "Opening Matrix")
        return
    def openBedrockWebsite(self):
        runInTerm("xdg-open https://bedrocklinux.org/", "Opening Bedrock Linux website")
        return
    def openRepo(self):
        runInTerm("xdg-open https://github.com/StratOS-Linux/StratOS-iso", "Opening StratOS GitHub repository")
        return
    def openCredits(self):
        dialog = creditsWindow()
        if dialog.exec_():
            return
        
    def setupAutostart(self):
        # if autostart is enabled, then create the autostart file
        if self.autostartCheckBox.isChecked():
            # print("setupAutostart(): autostart is enabled")
            filePath = f"{HOME}/.config/autostart/maneki_neko.desktop"
            if self.autostartCheckbox.is_checked():
                with open(filePath,"w") as f:
                  fileContent=f"""
[Desktop Entry]
Type=Application
Name=StratOS Maneki-Neko
GenericName=Welcome Screen App
Comment=Welcome Screen Application for StratOS
Exec={WORK_DIR}/main.py
Icon={WORK_DIR}/src/png/logo.png
Comment=StratOS welcome screen
X-GNOME-Autostart-enabled=true
Path={WORK_DIR}
Terminal=false
StartupNotify=false
        """
            f.write(fileContent)
            print("setupAutostart(): create desktop file: OK")
            command = ["chmod", "+x", filePath] 
            run = subprocess.Popen(command)
            print("setupAutostart(): make desktop file executable: OK")
            print("Maneki Neko autostart Enabled")
            # update checkbox text for feedback
            self.autostartCheckBox.setText("Autostart Maneki Neko (Enabled)")

        else:
            try:
                os.remove(filePath)
                # update checkbox text for feedback
                self.autostartCheckBox.setText("Autostart Maneki Neko (Disabled)")
                print("setupAutostart(): remove: Maneki Neko autostart Disabled")
            except Exception as E:
                print("setupAutostart(): remove: desktop file was not found anyway")
                self.autostartCheckBox.setText("Autostart Maneki Neko")

        return
    

class creditsWindow(QDialog):
    def __init__(self):
        # init the class and the ui file
        super(creditsWindow,self).__init__()
        loadUi(WORK_DIR + "/src/ui/creditsDialog.ui",self)

        self.openBedrockSiteButton.clicked.connect(self.openBedrockWebsite)
        self.openGithubRepo.clicked.connect(self.openRepo)

        return


class installDialog(QDialog):
    def __init__(self):
        super(installDialog,self).__init__()
        loadUi(WORK_DIR + "/src/ui/installDialog.ui", self)
        self.cancelButton.clicked.connect(self.reject)
        self.updateInstallQueueLabel()
        self.proceedButton.clicked.connect(self.invokeInstallScript)

    def updateInstallQueueLabel(self):
        if len(programInstallQueue) == 1:
            self.headingLabel.setText("You're about to install 1 program.")
            self.commentLabel.setText("The program you selected is:")

        else:
            self.headingLabel.setText(f"You're about to install {len(programInstallQueue)} programs.")
            self.commentLabel.setText("The programs you selected are:")

        installQueueString = ""
        for category in programInstallQueue:
            for app in category:
                installQueueString += f"• {app}\n"
        # print this string as textlabel
                
        self.installQueueLabel.setText(installQueueString)
                
        return
    
    def invokeInstallScript(self):
        global programInstallQueue, programSRCPreference
        print("Installing programs")

        self.accept()
        return
    



if __name__ == "__main__":
    main()