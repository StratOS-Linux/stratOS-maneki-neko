#!/usr/bin/env python

#Modules
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,  QApplication,  QDialog, QMessageBox, QLabel
from time import sleep
from os.path import isfile
import subprocess
import sys
import os
import time
import json


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
# Terminal invocation utility
def invoke_in_terminal(command_args, *, cwd=None, env=None, raise_on_error=False, shell_type="auto"):
    """
    Run a command in a new terminal window using DEFAULT_TERMINAL, fallback to xfce4-terminal if needed.
    Returns a dict: { 'success': bool, 'exit_code': int, 'error': Exception or None }
    If raise_on_error is True, raises exception on failure.
    
    Args:
        command_args: List of command arguments or single command string
        shell_type: "auto", "python", "bash", or "direct"
                   - "auto": Auto-detect based on file extension
                   - "python": Execute with python interpreter
                   - "bash": Execute with bash shell
                   - "direct": Execute command directly (original behavior)
    """
    import subprocess
    import os
    
    # Process command based on shell_type
    if isinstance(command_args, list) and len(command_args) > 0:
        first_arg = command_args[0]
        
        # Auto-detect shell type if not specified
        if shell_type == "auto":
            if first_arg.endswith('.py'):
                shell_type = "python"
            elif first_arg.endswith('.sh'):
                shell_type = "bash"
            else:
                shell_type = "direct"
        
        # Prepare command based on shell type
        if shell_type == "python":
            # For Python files, use python interpreter
            if len(command_args) == 1:
                # Single Python file
                final_command = f"python3 '{first_arg}'; echo 'Press Enter to close...'; read"
            else:
                # Python file with arguments - escape quotes in JSON strings
                escaped_args = []
                for arg in command_args[1:]:
                    if arg.startswith('{') or arg.startswith('['):
                        # This is likely a JSON string, escape it properly
                        escaped_arg = arg.replace('"', '\\"')
                        escaped_args.append(f'"{escaped_arg}"')
                    else:
                        escaped_args.append(f"'{arg}'")
                args_str = ' '.join(escaped_args)
                final_command = f"python3 '{first_arg}' {args_str}; echo 'Press Enter to close...'; read"
        elif shell_type == "bash":
            # For shell scripts, use bash
            if len(command_args) == 1:
                final_command = f"bash '{first_arg}'; echo 'Press Enter to close...'; read"
            else:
                args_str = ' '.join(f"'{arg}'" for arg in command_args[1:])
                final_command = f"bash '{first_arg}' {args_str}; echo 'Press Enter to close...'; read"
        else:
            # Direct execution (original behavior)
            final_command = ' '.join(f"'{arg}'" for arg in command_args) + "; echo 'Press Enter to close...'; read"
    else:
        # Handle string command
        final_command = str(command_args) + "; echo 'Press Enter to close...'; read"
    
    terminal = globals().get('DEFAULT_TERMINAL', 'x-terminal-emulator')
    fallback_terminal = 'xfce4-terminal'
    
    # Terminal-specific command formatting
    def format_terminal_command(term, cmd):
        if 'xfce4-terminal' in term:
            return [term, '--command', f'bash -c "{cmd}"']
        elif 'gnome-terminal' in term:
            return [term, '--', 'bash', '-c', cmd]
        elif 'konsole' in term:
            return [term, '-e', 'bash', '-c', cmd]
        elif 'xterm' in term:
            return [term, '-e', 'bash', '-c', cmd]
        else:
            # Generic fallback
            return [term, '-e', 'bash', '-c', cmd]
    
    primary_args = format_terminal_command(terminal, final_command)
    fallback_args = format_terminal_command(fallback_terminal, final_command)
    
    try:
        proc = subprocess.Popen(primary_args, cwd=cwd, env=env)
        proc.wait()
        exit_code = proc.returncode
        if exit_code == 0:
            return {'success': True, 'exit_code': exit_code, 'error': None}
        else:
            proc2 = subprocess.Popen(fallback_args, cwd=cwd, env=env)
            proc2.wait()
            exit_code2 = proc2.returncode
            if exit_code2 == 0:
                return {'success': True, 'exit_code': exit_code2, 'error': None}
            else:
                if raise_on_error:
                    raise subprocess.CalledProcessError(exit_code2, primary_args)
                return {'success': False, 'exit_code': exit_code2, 'error': None}
    except Exception as e:
        try:
            proc2 = subprocess.Popen(fallback_args, cwd=cwd, env=env)
            proc2.wait()
            exit_code2 = proc2.returncode
            if exit_code2 == 0:
                return {'success': True, 'exit_code': exit_code2, 'error': None}
            else:
                if raise_on_error:
                    raise subprocess.CalledProcessError(exit_code2, fallback_args)
                return {'success': False, 'exit_code': exit_code2, 'error': e}
        except Exception as e2:
            if raise_on_error:
                raise e2
            return {'success': False, 'exit_code': None, 'error': e2}

import json
app = QApplication(sys.argv)

# global variable used to count number of errors until time to display error popup message
# each time error occurs, this variable gets decremented
# if its zero, the error message is displayed.



# Load packageSRCReference from external JSON file
json_path = os.path.join(os.getcwd(), "src/stratos-packages.json")
with open(json_path, "r") as f:
    packageSRCReference = json.load(f)

# Get terminal emulator from $TERM or fallback
DEFAULT_TERMINAL = os.environ.get("TERM", "x-terminal-emulator")


AURInstallQueue = None
FLATPAKInstallQueue = None
PACMANInstallQueue = None
programSRCPreference = {}   # list of all apps with the selected source for installation
programInstallQueue = []    # list of all apps selected for install
programInstallQueueLen = 0  # number of all apps selected for install, 0 is temporary value and
                            # will be updated when proceeding to install

defaultAPPSList = []        # list of all the default apps marked for installation
                            # these defaults can be changed inside the welcomeScreen() class

lastPage=3  # the last page of the app is the 3rd page
            # 1st-> welcome page    2nd-> overview on Stratos   3rd -> last page with buttons to install programs, distro etc
            # 4th-> program installer

WORK_DIR = os.getcwd() # gets working directory of the python script
                       # at install location value shoulda be /opt/maneki-neko
                       # to HARDCODE this , change WORK_DIR to /opt/maneki-neko





# ===============================================================================================================

#  __  __                  _    _   _   _      _         
# |  \/  | __ _ _ __   ___| | _(_) | \ | | ___| | _____  
# | |\/| |/ _` | '_ \ / _ \ |/ / | |  \| |/ _ \ |/ / _ \ 
# | |  | | (_| | | | |  __/   <| | | |\  |  __/   < (_) |
# /_/   \_\ .__/| .__/|_|_|\___|_|\_\_| |_| \_|\___|_|\_\___/ 
                                                       
#     _                _ _           _   _             
#    / \   _ __  _ __ | (_) ___ __ _| |_(_) ___  _ __  
#   / _ \ | '_ \| '_ \| | |/ __/ _` | __| |/ _ \| '_ \ 
#  / ___ \| |_) | |_) | | | (_| (_| | |_| | (_) | | | |
# /_/   \_\ .__/| .__/|_|_|\___\__,_|\__|_|\___/|_| |_|
#         |_|   |_|                                      


class welcomeScreen(QMainWindow):

    # CLASS variables
    defaultWEBlist     = ['librewolf']                 # list of all Web browsers marked for install by DEFAULT
    defaultMEDIAlist   = ['vlc']                       # list of all Media players marked for install by DEFAULT
    defaultOFFICElist  = ['onlyoffice']                # list of all Office Suites marked for install by DEFAULT
    defaultTXTlist     = ['stratmacs']                 # list of all Text Editors marked for install by DEFAULT
    defaultMISClist    = ['evince']                    # list of all Miscellaneous programs marked for install by DEFAULT
    
    AURInstallQueue = None
    FLATPAKInstallQueue = None
    PACMANInstallQueue = None

    def __init__(self):
        global defaultAPPSList
        # init the class
        super(welcomeScreen,self).__init__()
        # load the ui file
        loadUi(WORK_DIR + "/src/ui/welcomeScreen.ui",self)
        defaultAPPSList = self.defaultWEBlist + self.defaultMEDIAlist + self.defaultOFFICElist + self.defaultTXTlist + self.defaultMISClist
        # always init window to first page
        self.windowStackedWidget.setCurrentIndex(0)
        # if AUTOSTART already enabled, then update the text of the autostartCheckBox
        self.updateAutostartCheckBoxState()
        
        # Buttons
        self.nextButton.clicked.connect(self.moveForward)   # also self.proceedToInstall
        self.backButton.clicked.connect(self.moveBackward)  
        self.distroInstallerButton.clicked.connect(self.runDistroInstallerScript)
        self.openDISCORDbutton.clicked.connect(self.openDISCORD_Link)
        self.openMASTODONbutton.clicked.connect(self.openMASTODON_Link)
        self.openMATRIXbutton.clicked.connect(self.openMATRIX_Website)
        self.autostartCheckBox.clicked.connect(self.setupAutostart)
        self.creditsButton.clicked.connect(self.openCreditsDialog)
        self.changeSettingsButton.clicked.connect(self.openchangeDefaultSettingsDialog)

    

        # package-installer page related-stuffs
        self.packageInstallerButton.clicked.connect(self.openPackageInstallerPage)
        self.MISClistWidget.itemClicked.connect(self.setMISCDescription)
        self.WEBlistWidget.itemClicked.connect(self.setWEBDescription)
        self.TXTlistWidget.itemClicked.connect(self.setTXTDescription)
        self.MEDIAlistWidget.itemClicked.connect(self.setMEDIADescription)
        self.OFFICElistWidget.itemClicked.connect(self.setOFFICEDescription)
        
        # functions to tell GUI to auto select default apps to be installed
        # refers to the ABOVE DEFINED CLASS VARIABLES
        self.selectDefaultApps()
        return

    def updateProgramSRCPreference(self):
        global programSRCPreference

        # for Brave
        if self.braveAURButton.isChecked():
            programSRCPreference['brave'] = 'aur'
        
        elif self.braveFLATPAKButton.isChecked():
            programSRCPreference['brave'] = 'flatpak'
      
        
        # for Chromium
        if self.chromiumFLATPAKButton.isChecked():
            programSRCPreference['chromium'] = 'flatpak'
        
        elif self.chromiumPACMANButton.isChecked():
            programSRCPreference['chromium'] = 'pacman'
        
        # for Firefox
        if self.firefoxFLATPAKButton_4.isChecked():
            programSRCPreference['firefox'] = 'flatpak'
        
        elif self.firefoxPACMANButton_4.isChecked():
            programSRCPreference['firefox'] = 'pacman'
        
        # for LibreWolf
        if self.librewolfAURButton.isChecked():
            programSRCPreference['librewolf'] = 'aur'
        
        elif self.librewolfFLATPAKButton.isChecked():
            programSRCPreference['librewolf'] = 'flatpak'

        # for VLC
        if self.vlcAURButton.isChecked():
            programSRCPreference['vlc'] = 'aur'
        
        elif self.vlcFLATPAKButton.isChecked():
            programSRCPreference['vlc'] = 'flatpak'
        
        elif self.vlcPACMANButton.isChecked():
            programSRCPreference['vlc'] = 'pacman'

        # for MPV
        if self.mpvAURButton.isChecked():
            programSRCPreference['mpv'] = 'aur'
        
        elif self.mpvFLATPAKButton.isChecked():
            programSRCPreference['mpv'] = 'flatpak'
        
        elif self.mpvPACMANButton.isChecked():
            programSRCPreference['mpv'] = 'pacman'

        # for OnlyOffice
        if self.onlyofficeAURButton.isChecked():
            programSRCPreference['onlyoffice'] = 'aur'
        
        elif self.onlyofficeFLATPAKButton.isChecked():
            programSRCPreference['onlyoffice'] = 'flatpak'
        
        # for LibreOffice
        if self.libreofficeFLATPAKButton.isChecked():
            programSRCPreference['libreoffice'] = 'flatpak'
        
        elif self.libreofficePACMANButton.isChecked():
            programSRCPreference['libreoffice'] = 'pacman'
        
        
        # for VSCodium
        if self.vscodiumAURButton.isChecked():
            programSRCPreference['vscodium'] = 'aur'
        
        elif self.vscodiumFLATPAKButton.isChecked():
            programSRCPreference['vscodium'] = 'flatpak'

        # for Atril
        if self.atrilPACMANButton.isChecked():
            programSRCPreference['atril'] = 'pacman'

        # for Evince
        if self.evincePACMANButton.isChecked():
            programSRCPreference['evince'] = 'pacman'


        # for Github Desktop
        if self.githubDesktopAURButton.isChecked():
            programSRCPreference['github'] = 'aur'
        
        # for Obsidian
        if self.obsidianAURButton.isChecked():
            programSRCPreference['obsidian'] = 'aur'
        
        elif self.obsidianPACMANButton.isChecked():
            programSRCPreference['obsidian'] = 'pacman'


        # these custom StratOS programs have ONLY ONE software source i.e. PACMAN
        # these custom Programs also use custom install scripts to install their themes and modules =========================
        programSRCPreference['stratvim'] = 'script'
        programSRCPreference['stratmacs'] = 'script'
        # ===================================================================================================================


        # gsconnect only has an AUR for Arch stratum
        programSRCPreference['gsconnect'] = 'aur'

        return

    def proceedToInstall(self):
        global programInstallQueue, programSRCPreference, packageSRCReference, programInstallQueueLen, AURInstallQueue, FLATPAKInstallQueue, PACMANInstallQueue
        sleep(0.3)
        # clear list if not empty
        if programInstallQueue != []:
            programInstallQueue == []

        # update values in program install queue
        WEBprogramInstallQueue = []
        # for every item listed in the listwidget
        for i in range(0,self.WEBlistWidget.count()):
            item = self.WEBlistWidget.item(i)
            # if the current item is checked
            if item.checkState() == QtCore.Qt.Checked:
                # append the program name to the list
                WEBprogramInstallQueue.append(item.text().lower())

        MEDIAprogramInstallQueue = []
        for i in range(0,self.MEDIAlistWidget.count()):
            item = self.MEDIAlistWidget.item(i)
            # if the current item is checked
            if item.checkState() == QtCore.Qt.Checked:
                # append the program name to the list
                MEDIAprogramInstallQueue.append(item.text().lower())

        OFFICEprogramInstallQueue = []
        for i in range(0,self.OFFICElistWidget.count()):
            item = self.OFFICElistWidget.item(i)
            # if the current item is checked
            if item.checkState() == QtCore.Qt.Checked:
                # append the program name to the list
                OFFICEprogramInstallQueue.append(item.text().lower())

        TXTprogramInstallQueue = []
        for i in range(0,self.TXTlistWidget.count()):
            item = self.TXTlistWidget.item(i)
            # if the current item is checked
            if item.checkState() == QtCore.Qt.Checked:
                # append the program name to the list
                TXTprogramInstallQueue.append(item.text().lower().split()[0])
   
        MISCprogramInstallQueue = []
        for i in range(0,self.MISClistWidget.count()):
            item = self.MISClistWidget.item(i)
            # if the current item is checked
            if item.checkState() == QtCore.Qt.Checked:
                # append the program name to the list
                MISCprogramInstallQueue.append(item.text().lower().split()[0])

        # update the class variable
        programInstallQueue =   \
            WEBprogramInstallQueue + MEDIAprogramInstallQueue + OFFICEprogramInstallQueue +    \
                    TXTprogramInstallQueue + MISCprogramInstallQueue 
        

        programInstallQueueLen = len(programInstallQueue)

        # if programQueue is empty ie not filled
        # send popup message and exit function
        if programInstallQueueLen == 0:
            self.errorMessageBox(title = 'Cannot Install', message = 'No programs marked for install', icon = 'warn')
            return
        # now call function to determine selected sources
        self.updateProgramSRCPreference()

        # prepare program install queues (global var)


        AURInstallQueue      = {"aur"       : [packageSRCReference["aur"][p]        for p,v in programSRCPreference.items() if v == "aur"      and p in programInstallQueue ]}
        FLATPAKInstallQueue  = {"flatpak"   : [packageSRCReference["flatpak"][p]    for p,v in programSRCPreference.items() if v == "flatpak"  and p in programInstallQueue ]}
        PACMANInstallQueue   = {"pacman"    : [packageSRCReference["pacman"][p]     for p,v in programSRCPreference.items() if v == "pacman"   and p in programInstallQueue ]}

        # now call the install dialog
        dialog = installDialog(self)
        if dialog.exec_():
            return

    def selectDefaultApps(self):

        for i in range(0,self.WEBlistWidget.count()):
            item = self.WEBlistWidget.item(i)
            # check if the current list widget item (ie package) is in the list of default packages
            # marked for install
            if item.text().lower()in self.defaultWEBlist:
                item.setCheckState(QtCore.Qt.Checked)
  
        for i in range(0,self.MEDIAlistWidget.count()):
            item = self.MEDIAlistWidget.item(i)
            # check if the current list widget item (ie package) is in the list of default packages
            # marked for install
            if item.text().lower()in self.defaultMEDIAlist:
                item.setCheckState(QtCore.Qt.Checked)
     

        for i in range(0,self.OFFICElistWidget.count()):
            item = self.OFFICElistWidget.item(i)
            # check if the current list widget item (ie package) is in the list of default packages
            # marked for install
            if item.text().lower()in self.defaultOFFICElist:
                item.setCheckState(QtCore.Qt.Checked)
  

        for i in range(0,self.TXTlistWidget.count()):
            item = self.TXTlistWidget.item(i)
            # check if the current list widget item (ie package) is in the list of default packages
            # marked for install
            if item.text().lower().split()[0] in self.defaultTXTlist:
                item.setCheckState(QtCore.Qt.Checked)


        for i in range(0,self.MISClistWidget.count()):
            item = self.MISClistWidget.item(i)
            # check if the current list widget item (ie package) is in the list of default packages
            # marked for install
            if item.text().lower().split()[0] in self.defaultMISClist:
                item.setCheckState(QtCore.Qt.Checked)
        return

    def setMISCDescription(self):
        # function that shows details of selected package on description widget of MISC category
        refDict = { "atril"     : 11,    \
                    "evince"    : 12,    \
                    "github"    : 13,    \
                    "obsidian"  : 14,    \
                    "gsconnect" : 15
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items fully
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

    def setWEBDescription(self):
        # function that shows details of selected package on description widget of WEB category
        refDict = { "firefox"     : 0,    \
                    "chromium"    : 1,    \
                    "librewolf"   : 2,    \
                    "brave"       : 3
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items fully
        try:
        # to determine the selected app
            selectedApp = self.WEBlistWidget.currentItem().text().lower()
        # EXPLANATION: suppose I selected "Atril PDF Document Viewer"
        # 1. self.MISClistWidget.currentItem().text() = "Atril PDF Document Viewer"
        # 2. self.MISClistWidget.currentItem().text().lower() = "atril pdf document viewer"
        # 3. self.MISClistWidget.currentItem().text().lower().split() = ["atril", "pdf","document", "viewer"]
        # 4. self.MISClistWidget.currentItem().text().lower().split()[0] = "atril"
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return

    def setTXTDescription(self):
        # function that shows details of selected package on description widget of TXT category
        refDict = { "stratmacs"   : 8,    \
                    "stratvim"    : 9,    \
                    "vscodium"    : 10
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items fully
        try:
        # to determine the selected app
            selectedApp = self.TXTlistWidget.currentItem().text().lower().split()[0]
        # EXPLANATION: suppose I selected "Atril PDF Document Viewer"
        # 1. self.MISClistWidget.currentItem().text() = "Atril PDF Document Viewer"
        # 2. self.MISClistWidget.currentItem().text().lower() = "atril pdf document viewer"
        # 3. self.MISClistWidget.currentItem().text().lower().split() = ["atril", "pdf","document", "viewer"]
        # 4. self.MISClistWidget.currentItem().text().lower().split()[0] = "atril"
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return

    def setMEDIADescription(self):
        # function that shows details of selected package on description widget of TXT category
        refDict = { "vlc"   : 4,    \
                    "mpv"   : 5
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items fully
        try:
        # to determine the selected app
            selectedApp = self.MEDIAlistWidget.currentItem().text().lower()
        # EXPLANATION: suppose I selected "Atril PDF Document Viewer"
        # 1. self.MISClistWidget.currentItem().text() = "Atril PDF Document Viewer"
        # 2. self.MISClistWidget.currentItem().text().lower() = "atril pdf document viewer"
        # 3. self.MISClistWidget.currentItem().text().lower().split() = ["atril", "pdf","document", "viewer"]
        # 4. self.MISClistWidget.currentItem().text().lower().split()[0] = "atril"
            self.packageDetailsStackedWidget.setCurrentIndex(refDict[selectedApp])
        except AttributeError:
            pass
        return

    def setOFFICEDescription(self):
        # function that shows details of selected package on description widget of TXT category
        refDict = { "onlyoffice"    : 6,    \
                    "libreoffice"   : 7
                }
        # using try-except block to avoid error if user directly ticks the options without selecting the items fully
        try:
        # to determine the selected app
            selectedApp = self.OFFICElistWidget.currentItem().text().lower()
        # EXPLANATION: suppose I selected "Atril PDF Document Viewer"
        # 1. self.MISClistWidget.currentItem().text() = "Atril PDF Document Viewer"
        # 2. self.MISClistWidget.currentItem().text().lower() = "atril pdf document viewer"
        # 3. self.MISClistWidget.currentItem().text().lower().split() = ["atril", "pdf","document", "viewer"]
        # 4. self.MISClistWidget.currentItem().text().lower().split()[0] = "atril"
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

    def runDistroInstallerScript(self):
        if not isfile('/usr/local/bin/StratOS-configure-distro'):
            self.errorMessageBox(title = 'Cannot Open DistroInstaller', message = ' Maneki could not open helper program to install distros on StratOS.', details = "/usr/local/bin/StratOS-configure-distro: No such file or directory", icon = 'critical')
            return
        print("runDistroInstaller(): executing the installer script")
        result = invoke_in_terminal(['/usr/local/bin/StratOS-configure-distro'])
        if not result['success']:
            self.errorMessageBox(title = 'Cannot Open DistroInstaller', message = 'Failed to launch installer script.', details = str(result['error']), icon = 'critical')
        return

    def openPackageInstallerPage(self):
        # change the page
        currentIndex = self.windowStackedWidget.currentIndex()
        self.windowStackedWidget.setCurrentIndex(currentIndex+1)
        # morph Next button to install button

        self.morphNextButton()
        return

    def errorMessageBox(self, title, message, details = None, icon = "info"):

        if icon == "info":
            msg = QMessageBox(1, title, message, QMessageBox.Ok,icon = QMessageBox.Information, parent = self)
        elif icon == "warn":
            msg = QMessageBox(1, title, message, QMessageBox.Ok,icon = QMessageBox.Warning, parent = self)
        elif icon == "critical":
            print('\a')
            msg = QMessageBox(1, title, message, QMessageBox.Ok,icon = QMessageBox.Critical, parent = self)

        if details:
            msg.setDetailedText(details)

        msg.setDefaultButton(QMessageBox.Ok)
        msg.setStyleSheet("""                             
            QWidget{
	            background-color: rgb(30, 31, 47);
	            color: rgb(118, 159, 240);
            }
            QPushButton{font-size:16px;}


            QPushButton:hover {
                background-color: #3b4261;
            }

            QPushButton:pressed {
                background-color: #414868;
            }
                                                """)
        msg.exec()

    def openWebsite(self):
        # command to open the URL
        command = ["xdg-open", "https://stratos-linux.org"]
        run = subprocess.Popen(command)
        return

    def openchangeDefaultSettingsDialog(self):
        dialog = changeDefaultSettingsDialog(self)
        
        if dialog.exec_():
            programInstallerOpened = dialog.programInstallerOpened

            if programInstallerOpened == True:
                self.windowStackedWidget.setCurrentIndex(3)
                self.morphNextButton()
            return

    def openMASTODON_Link(self):
        # command to open the URL
        command = ["xdg-open", "https://fosstodon.org/@StratOS"]
        run = subprocess.Popen(command)

        return

    def openMATRIX_Website(self):
        # command to open the URL
        command = ["xdg-open", "https://matrix.to/#/#stratos:matrix.org"]
        run = subprocess.Popen(command)

        return
    
    def openDISCORD_Link(self):
        # command to open the URL
        command = ["xdg-open", "https://discord.com/invite/DVaXRCnCet"]
        run = subprocess.Popen(command)

        return  

    def openCreditsDialog(self):
        dialog = creditsWindow(self)
        if dialog.exec_():
            return

    def setupAutostart(self):
        global errorCount
        # define home and hence the full file path for the DESKTOP FILE
        home = os.path.expanduser("~")

        # path of the EXECUTABLE in DESKTOP file
        EXEC_PATH = WORK_DIR + "/main.py"   
        # to HARDCODE to /usr/local/bin/maneki-neko, just change the EXEC_PATH variable
        # ideal case is to just run this script from /opt/maneki-neko installation folder
        # the same desktop file in autostart folder can be used to create MENU ENTRY for maneki neko
        
        filePath = home + "/.config/autostart/maneki_neko.desktop" # full path to desktop file
        
        # create the desktop file and save it in $HOME/.config/autostart when the checkBox is checked
        if self.autostartCheckBox.isChecked():
            # opening the file in write mode

            try:
                with open(filePath,"w") as f:

                    fileContent=f"""
[Desktop Entry]
Type=Application
Name=StratOS Maneki-Neko
GenericName=Welcome Screen App
Comment=Welcome Screen Application for StratOS
Exec={EXEC_PATH}
Icon={WORK_DIR}/src/png/maneki_neko.png
Comment=StratOS Welcome Screen Application
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

                print("setupAutostart(): Maneki Neko autostart Enabled")

                # update checkbox text for feedback
                self.autostartCheckBox.setText("Autostart Maneki Neko (Enabled)")
            except FileNotFoundError as E404:
                self.errorMessageBox(title = 'Cannot Enable Autostart', message = ' Maneki could not create desktop file for autostart.', details = E404, icon = 'critical')
                print("setupAutostart(): Maneki could not create desktop file for autostart.")
                print(f"setupAutostart(): ERROR: {E404}\n")
                self.autostartCheckBox.toggle()

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



# =================================================================================================

#  ____                          __        ___           _                   
# |  _ \ ___  _ __  _   _ _ __   \ \      / (_)_ __   __| | _____      _____ 
# | |_) / _ \| '_ \| | | | '_ \   \ \ /\ / /| | '_ \ / _` |/ _ \ \ /\ / / __|
# |  __/ (_) | |_) | |_| | |_) |   \ V  V / | | | | | (_| | (_) \ V  V /\__ \
# |_|   \___/| .__/ \__,_| .__/     \_/\_/  |_|_| |_|\__,_|\___/ \_/\_/ |___/
#            |_|         |_|                                                 

class creditsWindow(QDialog):
    def __init__(self, parent = None):
        # init the class and the ui file
        super(creditsWindow,self).__init__()
        loadUi(WORK_DIR + "/src/ui/creditsDialog.ui",self)

        self.openBedrockSiteButton.clicked.connect(self.openBedrockWebsite)
        self.openGithubRepo.clicked.connect(self.openRepo)

        return
    
    def openBedrockWebsite(self):
        # the command to open the website
        command = ['xdg-open', 'https://bedrocklinux.org/']

        # run the command
        run = subprocess.Popen(command)
        return

    def openRepo(self):
        # the command to open the website
        command = ['xdg-open', 'https://github.com/stratos-linux']

        # run the command
        run = subprocess.Popen(command)
        return


class installDialog(QDialog):
    import asyncio

    

    AURInstallQueue = None
    FLATPAKInstallQueue = None
    PACMANInstallQueue = None
    installFlatpaksSystemWide = True
    isThereFlatpak = True
    isTherePacman = True
    isThereAUR = True

    def __init__(self, parent = None):
        global AURInstallQueue, FLATPAKInstallQueue, PACMANInstallQueue
        self.AURInstallQueue        = AURInstallQueue
        self.PACMANInstallQueue     = PACMANInstallQueue
        self.FLATPAKInstallQueue    = FLATPAKInstallQueue 

        super(installDialog,self).__init__()
        loadUi(WORK_DIR + "/src/ui/installDialog.ui", self)
        self.dialogStackedWidget.setCurrentIndex(0)
        self.cancelButton.clicked.connect(self.reject)
        self.updateInstallQueueLabel()
        
        
        self.proceedButton.clicked.connect(self.invokeInstallScript)
        # set these status variables to false
        # if no AUR packages marked for install
        self.isThereAUR = False if len(self.AURInstallQueue["aur"]) == 0 else True
        # if no FLATPAK packages marked for install
        self.isThereFlatpak = False if len(self.FLATPAKInstallQueue["flatpak"]) == 0 else True
        # if no PACMAN packages marked for install
        self.isTherePacman = False if len(self.PACMANInstallQueue["pacman"]) == 0 else True
        if not self.isThereFlatpak:
            self.flatpakSudoLabel.setEnabled(False)
            self.sudoCheckBox.setEnabled(False)
            self.sudoCheckBox.setText("No Flatpaks marked for install")
        else:
            self.flatpakSudoLabel.setEnabled(True)
            self.sudoCheckBox.setEnabled(True)
        
        self.sudoCheckBox.toggled.connect(self.setFlatpakInstallPreference)

                




    def setFlatpakInstallPreference(self):
        self.installFlatpaksSystemWide = self.sudoCheckBox.isChecked()
        if self.installFlatpaksSystemWide:
            self.sudoCheckBox.setText("Yes, install packages system-wide")
        else:
            self.sudoCheckBox.setText("No, install packages for me only. (user-space)")
        return

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
        """Launch the package installer script with package data as arguments."""
        try:
            # Prepare package data - extract the actual package lists from the dictionaries
            aur_packages = self.AURInstallQueue.get("aur", []) if self.AURInstallQueue else []
            pacman_packages = self.PACMANInstallQueue.get("pacman", []) if self.PACMANInstallQueue else []
            flatpak_packages = self.FLATPAKInstallQueue.get("flatpak", []) if self.FLATPAKInstallQueue else []
            
            print(f"🚀 Debug - AUR queue: {self.AURInstallQueue}")
            print(f"🚀 Debug - Pacman queue: {self.PACMANInstallQueue}")
            print(f"🚀 Debug - Flatpak queue: {self.FLATPAKInstallQueue}")
            print(f"🚀 Debug - Extracted AUR packages: {aur_packages}")
            print(f"🚀 Debug - Extracted Pacman packages: {pacman_packages}")
            print(f"🚀 Debug - Extracted Flatpak packages: {flatpak_packages}")
            
            # Create JSON string for combined packages
            package_data = {
                'aur': aur_packages,
                'pacman': pacman_packages,
                'flatpak': flatpak_packages
            }
            packages_json = json.dumps(package_data)
            
            print(f"🚀 Debug - Final JSON: {packages_json}")
            print(f"🚀 Debug - installFlatpaksSystemWide: {self.installFlatpaksSystemWide}")
            
            # Path to the installer script
            installer_script = os.path.join(WORK_DIR, "src", "scripts", "installscripts", "package_installer.py")
            
            # Prepare command arguments
            command_args = [installer_script, "--packages-json", packages_json]
            
            # Add flatpak system-wide installation flag if needed
            if self.installFlatpaksSystemWide:
                command_args.append("--ifsw")
            
            print(f"🚀 Launching installer with command: {command_args}")
            print(f"🚀 Flatpak installation scope: {'system-wide' if self.installFlatpaksSystemWide else 'user-only'}")
            
            # Launch installer script in terminal using python shell type
            result = invoke_in_terminal(command_args, shell_type="python")
            
            if result['success']:
                print("✅ Installer script launched successfully")
                self.accept()
            else:
                print(f"❌ Failed to launch installer script: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error launching installer script: {e}")
            import traceback
            traceback.print_exc()


class changeDefaultSettingsDialog(QDialog):

    programInstallerOpened = False


        # variable used to count number of errors in each function until time to display error popup message
        # each time error occurs, this variable gets decremented
        # if its zero, the error message is displayed.

    errorCount = {  "selectTextEditor"  : 2     ,\
                    "selectPDFViewer"   : 2     ,\
                    "selectDOCXEditor"  : 2     ,\
                    "selectPPTXEditor"  : 2     ,\
                    "selectXLSXEditor"  : 2     ,\
                    "openGNOMETweaks"   : 2     ,\
                    "openGNOMESettings" : 2     

                }

    def __init__(self, parent = None):
        

        super(changeDefaultSettingsDialog,self).__init__()
        loadUi(WORK_DIR + "/src/ui/changeDefaultsDialog.ui",self)
        
        # set dialog to ALWAYS SHOW THE MAIN PAGE OF DIALOG
        self.dialogStackedWidget.setCurrentIndex(0)
        
        self.primaryDialogButtonBox.rejected.connect(self.reject)
        self.primaryDialogButtonBox.accepted.connect(self.accept)
        self.primaryDialogButtonBox.helpRequested.connect(lambda: \
                                                          self.dialogStackedWidget.setCurrentIndex(1))
        
        self.previousButton.clicked.connect(lambda: \
                                            self.dialogStackedWidget.setCurrentIndex(0))
        
        self.helpPageButtonBox.accepted.connect(self.accept)
        self.helpPageButtonBox.rejected.connect(self.reject)

        self.openProgramInstallerButton.clicked.connect(self.closeDialogAndOpenInstaller)

        self.openGNOMETweaksButton.clicked.connect(self.openGNOMETweaks)
        self.openGNOMESettingsButton.clicked.connect(self.openGNOMESettings)
        self.selectTextEditorButton.clicked.connect(self.selectTextEditor)
        self.selectDOCXButton.clicked.connect(self.selectDOCXEditor)
        self.selectPPTXButton.clicked.connect(self.selectPPTXEditor)
        self.selectXLSXButton.clicked.connect(self.selectXLSXEditor)
        self.selectPDFButton.clicked.connect(self.selectPDFViewer)


    def errorMessageBox(self, title, message, function,details = None):


        if self.errorCount[function] > 0:
            self.errorCount[function] -= 1
            return
        else:
            self.errorCount[function] = 2
            msg = QMessageBox(1, title, message, QMessageBox.Ok,icon = QMessageBox.Critical, parent = self)

            if details:
                    msg.setDetailedText(str(details))
    
            msg.setDefaultButton(QMessageBox.Ok)
            msg.setStyleSheet("""                             
                QWidget{
	                background-color: rgb(30, 31, 47);
	                color: rgb(118, 159, 240);
                }
                QPushButton{font-size:16px;}


                QPushButton:hover {
                    background-color: #3b4261;
                }

                QPushButton:pressed {
                    background-color: #414868;
                }
                                                    """)
            msg.exec()

    def selectTextEditor(self):
        result = invoke_in_terminal([f"bash -c '{WORK_DIR}/src/scripts/mimeopenScripts/setDefaultTextEditor.sh'"])
        if not result['success']:
            self.errorMessageBox(title="Cannot Open",message="Cannot open terminal emulator...", details = str(result['error']), function = "selectTextEditor")
            print("selectTextEditor(): Couldn't run MIMEOPEN command to change default text editor... ")
        else:
            print("selectTextEditor(): Successfully ran MIMEOPEN command to change default text editor.")
            tmp = QMessageBox(0,"Success", "Successfully changed default text editor.")
            
        return

    def selectPDFViewer(self):
        result = invoke_in_terminal([f"bash -c '{WORK_DIR}/src/scripts/mimeopenScripts/setDefaultPDFApp.sh'"])
        if not result['success']:
            self.errorMessageBox(title="Cannot Open",message="Cannot open terminal emulator...", details = str(result['error']), function = "selectPDFViewer")
            print("selectPDFViewer(): Couldn't run MIMEOPEN command to change default PDF viewer... ")
        else:
            print("selectPDFViewer(): Successfully ran MIMEOPEN command to change default PDF viewer.")
            tmp = QMessageBox(0,"Success", "Successfully changed default PDF viewer.")
        return

    def selectDOCXEditor(self):
        result = invoke_in_terminal([f"bash -c '{WORK_DIR}/src/scripts/mimeopenScripts/setDefaultDOCXApp.sh'"])
        if not result['success']:
            self.errorMessageBox(title="Cannot Open",message="Cannot open terminal emulator...", details = str(result['error']), function = "selectDOCXEditor")
            print("selectDOCXEditor(): Couldn't run MIMEOPEN command to change default Word file editor... ")
        else:
            print("selectDOCXEditor(): Successfully ran MIMEOPEN command to change default Word file editor.")
            tmp = QMessageBox(0,"Success", "Successfully changed default Word file editor.")
        return

    def selectPPTXEditor(self):
        result = invoke_in_terminal([f"bash -c '{WORK_DIR}/src/scripts/mimeopenScripts/setDefaultPresentationApp.sh'"])
        if not result['success']:
            self.errorMessageBox(title="Cannot Open",message="Cannot open terminal emulator...", details = str(result['error']), function = "selectPPTXEditor")
            print("selectPPTXEditor(): Couldn't run MIMEOPEN command to change default Powerpoint file editor... ")
        else:
            print("selectPPTXEditor(): Successfully ran MIMEOPEN command to change default Powerpoint file editor.")
            tmp = QMessageBox(0,"Success", "Successfully changed default Powerpoint file editor.")
        return

    def selectXLSXEditor(self):
        result = invoke_in_terminal([f"bash -c '{WORK_DIR}/src/scripts/mimeopenScripts/setDefaultSpreadsheetApp.sh'"])
        if not result['success']:
            self.errorMessageBox(title="Cannot Open",message="Cannot open terminal emulator...", details = str(result['error']), function = "selectXLSXEditor")
            print("selectXLSXEditor(): Couldn't run MIMEOPEN command to change default Excel file editor... ")
        else:
            print("selectXLSXEditor(): Successfully ran MIMEOPEN command to change default Excel file editor.")
            tmp = QMessageBox(0,"Success", "Successfully changed default Excel file editor.")
        return



    def openGNOMESettings(self):
        command = ['gnome-control-center', 'default-apps']

        try:
            temporary = subprocess.Popen(command,stdout=subprocess.PIPE)
            
        except FileNotFoundError as E404:
            self.errorMessageBox(title="Cannot Open",message="Cannot open GNOME Settings...", details = E404, function = "openGNOMESettings")
            print(f"openGNOMESettings()[404]: Couldn't open Gnome Settings...:: {E404} ")

        return


    def openGNOMETweaks(self):

        command = ['gnome-tweaks', 'appearance']

        try:
            temporary = subprocess.Popen(command,stdout=subprocess.PIPE)
         
            
        except FileNotFoundError as E404:
            self.errorMessageBox(title="Cannot Open",message="Cannot open GNOME Tweaks...", details = E404, function = "openGNOMETweaks")
            print(f"openGNOMETweaks()[404]: Couldn't open Gnome Tweaks...:: {E404} ")

        return



    def closeDialogAndOpenInstaller(self):
       
        self.programInstallerOpened = True
        self.accept()
        return





# ========================================================================================================

#                             _                  
#             _ __ ___   __ _(_)_ __             
#            | '_ ` _ \ / _` | | '_ \            
#            | | | | | | (_| | | | | |           
#  _____ ____|_| |_| |_|\__,_|_|_| |_|____ _____ 
# |_____|_____|                     |_____|_____|

# globals
mainScreen = welcomeScreen()

def main():
    global app
    global mainScreen
    print("Program launch OK")
    mainScreen.setWindowIcon(QtGui.QIcon(WORK_DIR + "/src/png/maneki_neko.png"))
    mainScreen.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting...")
    
    return


if __name__ == "__main__":
    main()
