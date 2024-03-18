#!/usr/bin/env python

#Modules
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,  QApplication,  QDialog, QMessageBox
from time import sleep
import os, subprocess
HOME=os.path.expanduser("~")
WORK_DIR=os.path.dirname(os.path.abspath(__file__)) # the directory where the main.py file is located

#LICENSE
'''
StratOS-Maneki-Neko: Welcome Screen GUI Application for StratOS-Linux, written in Python and PyQt5
    Copyright (C) 2024  Adithya Sunil Kumar

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''


# globals
app = QApplication(sys.argv)

packageSRCReference = { # PACKAGE source reference dictionary

                        # IMP!! packageSRCReference != packageSRCPreference

                        # {"source1" : {"program1":"com.source1.Program1", "program2":"com.source1.Program2"}
                        # }

                        # ===== ALL FLATPAKS =====
                        "flatpak":{  # ======== BROWSERS ======== 
                                    "brave": "com.brave.Browser",                   
                                    "firefox": "org.mozilla.Firefox",               
                                    "chromium": "org.chromium.Chromium",            
                                    "librewolf": "io.gitlab.librewolf-community",   

                                    # ======== MEDIA PLAYERS ========
                                    "vlc" : "org.videolan.VLC",                     
                                    "mpv" : "io.mpv.Mpv",                           

                                    # ======== OFFICE PROGRAMS ========
                                    "libreoffice": "org.libreoffice.LibreOffice",   
                                    "onlyoffice": "org.onlyoffice.desktopeditors",  

                                    # ======== TEXT EDITORS ========
                                    "vscodium": "com.vscodium.codium"               

                                    # ======== MISCELLANEOUS ========
                                    # ====> NONE <==== for FLATPAK
                                }   ,                                               
                        
                        # ====== ALL ARCH USER REPOSITORY PROGRAMS ======
                        "aur" : {   # ======== BROWSERS ========
                                    "brave" : "brave-bin",                          
                                    "librewolf" : "librewolf-bin",                  
                                    
                                    # ======== MEDIA PLAYERS ========
                                    "mpv": "mpv-full",                              
                                    "vlc": "vlc-git",                               
                                    
                                    # ======== OFFICE PROGRAMS ========
                                    "onlyoffice": "onlyoffice-bin",                 
                                    
                                    # ======== TEXT EDITORS ========
                                    "vscodium": "vscodium-bin",                     
                                    
                                    # ======== MISCELLANEOUS ========
                                    "github" : "github-desktop-bin",                
                                    "obsidian" : "obsidian-bin"             
                                }   ,                                               
                        
                        # ===== ALL PACMAN PROGRAMS ========
                        "pacman":{  # ======= WEB BROWSERS ========
                                    "chromium": "chromium",                         
                                    "firefox": "firefox",                           

                                    # ======= MEDIA PLAYERS ========
                                    "vlc": "vlc",                                   
                                    "mpv": "mpv",                                   
                                    
                                    # ======= OFFICE SUITES ========               
                                    "libreoffice": "libreoffice-fresh",             
                                    
                                    # ======= TEXT EDITORS =======
                                    # ====> NONE <==== for PACMAN

                                    # ======= MISCELLANEOUS =======
                                    "atril": "atril",                               
                                    "evince": "evince",                             
                                    "obsidian": "obsidian"                          
                        }     
                        
        }

progSource = {}   # list of all apps with the selected mode for installation
programInstallQueue = []    # list of all apps selected for install
programInstallQueueLen = 0  # number of all apps selected for install, 0 is temporary value and
                            # will be updated when proceeding to install
defApps = []

lastPage=3  # the last page of the app is the 3rd page
            # 1st-> welcome page    2nd-> overview on Stratos   3rd -> last page with buttons to install programs, distro etc
            # 4th-> program installer

def runInTerm(cmd:str,mesg:str=None):
    if mesg: print(mesg)
    result = subprocess.Popen(["gnome-terminal", "--", cmd], stdout=subprocess.PIPE)
    out = result.communicate()
    return


class welcomeScreen(QMainWindow):

    # CLASS variables
    defBrowsers = ['librewolf']                 # list of all Web browsers marked for install by DEFAULT
    defPlayers  = []                            # list of all Media players marked for install by DEFAULT
    defOffice   = []                # list of all Office Suites marked for install by DEFAULT
    defEditors  = []                 # list of all Text Editors marked for install by DEFAULT
    defMisc     = []                            # list of all Miscellaneous programs marked for install by DEFAULT
    

    def __init__(self):
        global defApps
        # init the class
        super(welcomeScreen,self).__init__()
        # load the ui file
        loadUi(f"{WORK_DIR}/src/ui/welcomeScreen.ui",self)
        defApps = self.defBrowsers + self.defPlayers + self.defOffice + self.defEditors + self.defMisc
        # always init window to first page
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

        # package-installer page related-stuffs
        self.packageInstallerButton.clicked.connect(self.openPackageInstallerPage)
        self.MISClistWidget.itemClicked.connect(self.setMiscDesc)
        self.WEBlistWidget.itemClicked.connect(self.setWebDesc)
        self.TXTlistWidget.itemClicked.connect(self.setEdDesc)
        self.MEDIAlistWidget.itemClicked.connect(self.setMediaDesc)
        self.OFFICElistWidget.itemClicked.connect(self.setOfficeDesc)
        
        # functions to auto select default apps to be installed in UI
        self.selectDefaultApps()
        return

    def updateprogSource(self):
        global progSource

        # for Brave
        if self.braveAURButton.isChecked(): progSource['brave'] = 'aur'
        elif self.braveFLATPAKButton.isChecked(): progSource['brave'] = 'flatpak'
      
        
        # for Chromium
        if self.chromiumFLATPAKButton.isChecked(): progSource['chromium'] = 'flatpak'
        elif self.chromiumPACMANButton.isChecked(): progSource['chromium'] = 'pacman'
        
        # for Firefox
        if self.firefoxFLATPAKButton_4.isChecked(): progSource['firefox'] = 'flatpak'
        elif self.firefoxPACMANButton_4.isChecked(): progSource['firefox'] = 'pacman'
        
        # for LibreWolf
        if self.librewolfAURButton.isChecked(): progSource['librewolf'] = 'aur'
        elif self.librewolfFLATPAKButton.isChecked(): progSource['librewolf'] = 'flatpak'

        # for VLC
        if self.vlcAURButton.isChecked(): progSource['vlc'] = 'aur'
        elif self.vlcFLATPAKButton.isChecked(): progSource['vlc'] = 'flatpak'
        elif self.vlcPACMANButton.isChecked(): progSource['vlc'] = 'pacman'

        # for MPV
        if self.mpvAURButton.isChecked(): progSource['mpv'] = 'aur'
        elif self.mpvFLATPAKButton.isChecked(): progSource['mpv'] = 'flatpak'
        elif self.mpvPACMANButton.isChecked(): progSource['mpv'] = 'pacman'

        # for OnlyOffice
        if self.onlyofficeAURButton.isChecked(): progSource['onlyoffice'] = 'aur'
        elif self.onlyofficeFLATPAKButton.isChecked(): progSource['onlyoffice'] = 'flatpak'
        
        # for LibreOffice
        if self.libreofficeFLATPAKButton.isChecked(): progSource['libreoffice'] = 'flatpak'
        elif self.libreofficePACMANButton.isChecked(): progSource['libreoffice'] = 'pacman'

        # for VSCodium
        if self.vscodiumAURButton.isChecked(): progSource['vscodium'] = 'aur'
        elif self.vscodiumFLATPAKButton.isChecked(): progSource['vscodium'] = 'flatpak'
     

        # for Atril
        if self.atrilPACMANButton.isChecked(): progSource['atril'] = 'pacman'
        # for Evince
        if self.evincePACMANButton.isChecked(): progSource['evince'] = 'pacman'
        # for Github Desktop
        if self.githubDesktopAURButton.isChecked(): progSource['github'] = 'aur'
        
        # for Obsidian
        if self.obsidianAURButton.isChecked(): progSource['obsidian'] = 'aur'
        elif self.obsidianPACMANButton.isChecked(): progSource['obsidian'] = 'pacman'


        # these programs have ONLY ONE software source so hence putting None
        progSource['stratvim'] = None
        progSource['stratmacs'] = None
        progSource['gsconnect'] = None

        return

    def proceedToInstall(self):
        global programInstallQueue, programInstallQueueLen
        sleep(0.3)
        if programInstallQueue != []: programInstallQueue == []

        # update values in program install queue
        WEBprogramInstallQueue = []
        for i in range(0,self.WEBlistWidget.count()):
            item = self.WEBlistWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                WEBprogramInstallQueue.append(item.text().lower())

        MEDIAprogramInstallQueue = []
        for i in range(0,self.MEDIAlistWidget.count()):
            item = self.MEDIAlistWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                MEDIAprogramInstallQueue.append(item.text().lower())

        OFFICEprogramInstallQueue = []
        for i in range(0,self.OFFICElistWidget.count()):
            item = self.OFFICElistWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                OFFICEprogramInstallQueue.append(item.text().lower())

        TXTprogramInstallQueue = []
        for i in range(0,self.TXTlistWidget.count()):
            item = self.TXTlistWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                TXTprogramInstallQueue.append(item.text().lower().split()[0])
   
        MISCprogramInstallQueue = []
        for i in range(0,self.MISClistWidget.count()):
            item = self.MISClistWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                MISCprogramInstallQueue.append(item.text().lower().split()[0])

        # update the class variable
        programInstallQueue =   \
            WEBprogramInstallQueue + MEDIAprogramInstallQueue + OFFICEprogramInstallQueue +    \
                    TXTprogramInstallQueue + MISCprogramInstallQueue 
        

        programInstallQueueLen = len(programInstallQueue)
        if programInstallQueueLen == 0:
            message = QMessageBox.critical(self,"Cannot Install","No programs marked for install.")
            return
        self.updateprogSource()
        dialog = installDialog()
        if dialog.exec_():
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

    def setMiscDesc(self):
        # function that shows details of selected package on description widget of MISC catego
        refDict = { "atril"     : 11,    
                    "evince"    : 12,    
                    "github"    : 13,    
                    "obsidian"  : 14,    
                    "gsconnect" : 15
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items ful
        try:
        # to determine the selected app
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

    def setEdDesc(self):
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
        # purpose of this function is to update the text of 
        # autostart checkbox to Enabled if the desktop file already exists
        home = os.path.expanduser("~")
        filePath = home + "/.config/autostart/maneki_neko.desktop"
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

    def moveForward(self):
        global lastPage
        currentIndex = self.windowStackedWidget.currentIndex()
        sleep(0.1)
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

        self.windowStackedWidget.setCurrentIndex(currentIndex+1)
        self.backButton.setEnabled(True)


        # morph the button to "Exit" button on last page
        currentIndex = self.windowStackedWidget.currentIndex() #updated index of the window
        if currentIndex+1 == lastPage:
            self.morphNextButton()
        return

    def moveBackward(self):
        currentIndex = self.windowStackedWidget.currentIndex()
        sleep(0.1)
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
        runInTerm("/usr/local/bin/StratOS-configure-distro","Running the distro installer")
        return

    def openPackageInstallerPage(self):
        # change the page
        currentIndex = self.windowStackedWidget.currentIndex()
        self.windowStackedWidget.setCurrentIndex(currentIndex+1)
        # morph Next button to install button

        self.morphNextButton()
        return

    def runThemeChangerScript(self):
        runInTerm("/usr/local/bin/StratOS-configure-theme","Running the theme changer")
        return

    def runBrowserInstallerScript(self):
        runInTerm("/usr/local/bin/StratOS-configure-browser","Running the browser installer")
        return

    def openWebsite(self):
        runInTerm("xdg-open https://stratos-linux.github.io","Opening the website")
        return
    
    def openMastodon(self):
        runInTerm("xdg-open https://fosstodon.org/@stratos","Opening the Mastodon page")
        return

    def openMatrix(self):
        runInTerm("xdg-open https://matrix.to/#/#stratos:matrix.org","Opening the Matrix page")
        return
    
    def openDiscord(self):
        runInTerm("xdg-open https://discord.com/invite/DVaXRCnCet","Opening the Discord page")
        return  

    def openCredits(self):
        sleep(0.1)
        dialog = creditsWindow()
        if dialog.exec_():
            return

    def setupAutostart(self):
        filePath = f"{HOME}/.config/autostart/maneki_neko.desktop" # full path to desktop file
        
        # create the desktop file and save it in $HOME/.config/autostart when the checkBox is checked
        if self.autostartCheckBox.isChecked():
            # opening the file in write mode
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
                # end of with block
            print("setupAutostart(): create desktop file: OK")

            #make file executable
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



class creditsWindow(QDialog):
    def __init__(self):
        # init the class and the ui file
        super(creditsWindow,self).__init__()
        loadUi(f"{WORK_DIR}/src/ui/creditsDialog.ui",self)

        self.openBedrockSiteButton.clicked.connect(self.openBedrockWebsite)
        self.openGithubRepo.clicked.connect(self.openRepo)

        return
    
    def openBedrockWebsite(self):
        runInTerm("xdg-open https://bedrocklinux.org/","Opening the Bedrock Linux website")
        return

    def openRepo(self):
        runInTerm("xdg-open https://github.com/StratOS-Linux/StratOS-iso","Opening the StratOS GitHub repository")
        return


class installDialog(QDialog):
   

    def __init__(self):
        super(installDialog,self).__init__()
        loadUi(WORK_DIR + "/src/ui/installDialog.ui", self)
        self.cancelButton.clicked.connect(self.reject)
        self.updateInstallQueueLabel()
        self.proceedButton.clicked.connect(self.invokeInstallScript)

    def updateInstallQueueLabel(self):
        if programInstallQueueLen == 1:
            self.headingLabel.setText("You're about to install 1 program.")
            self.commentLabel.setText("The program you selected is:")

        else:
            self.headingLabel.setText(f"You're about to install {programInstallQueueLen} programs.")
            self.commentLabel.setText("The programs you selected are:")


        labelString = ""
        for app in programInstallQueue:
            labelString += app + ", " # append the app name to empty string
        
        # remove trailing space and comma
        labelString = labelString[:-2]

        self.installQueueLabel.setText(labelString)
        return
    
    def invokeInstallScript(self):
        global programInstallQueue, progSource, packageSRCReference
        # function that calls the external shell script to begin installation
        print("Installing programs....")

        AURInstallQueue      = {"aur"       : [packageSRCReference["aur"][p]        for p,v in progSource.items() if v == "aur"      and p in programInstallQueue ]}
        FLATPAKInstallQueue  = {"flatpak"   : [packageSRCReference["flatpak"][p]    for p,v in progSource.items() if v == "flatpak"  and p in programInstallQueue ]}
        PACMANInstallQueue   = {"pacman"    : [packageSRCReference["pacman"][p]     for p,v in progSource.items() if v == "pacman"   and p in programInstallQueue ]}

        aurString = ""
        for i in AURInstallQueue["aur"]: aurString += f"{i} "

        flatpakString = ""
        for i in FLATPAKInstallQueue["flatpak"]: flatpakString += f"{i} "

        pacmanString = ""
        for i in PACMANInstallQueue["pacman"]: pacmanString += f"{i} "

        if pacmanString: runInTerm(f"~/Git/StratOS/StratOS-iso/airootfs/usr/local/bin/install-using-pacman {pacmanString}")
        if aurString: runInTerm(f"~/Git/StratOS/StratOS-iso/airootfs/usr/local/bin/install-using-yay {aurString}")
        if flatpakString: runInTerm(f"~/Git/StratOS/StratOS-iso/airootfs/usr/local/bin/install-using-flatpak {flatpakString}")
        self.accept()
        return


if __name__ == "__main__":
    main()
