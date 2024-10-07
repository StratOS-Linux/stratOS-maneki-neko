import sys
import os
import pytest
from PyQt5.QtWidgets import QApplication
from unittest.mock import patch, MagicMock

# Add the root directory to the system path before importing or patching 'main'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def mock_loadUi(ui_file, self):
    # Set the attributes that are expected by creditsWindow
    self.openBedrockSiteButton = MagicMock()
    self.openBedrockSiteButton.clicked = MagicMock()
    self.openGithubRepo = MagicMock()
    self.openGithubRepo.clicked = MagicMock()

# Patch loadUi before importing main
with patch('PyQt5.uic.loadUi', side_effect=mock_loadUi):
    # Mock the welcomeScreen class to bypass UI components
    with patch('main.welcomeScreen', autospec=True):
        from main import creditsWindow

app = QApplication([])

@pytest.fixture
def credits_window():
    return creditsWindow()

@patch('subprocess.Popen')
def test_open_bedrock_website(mock_popen, credits_window):
    # Mock Popen so that no external commands run
    mock_popen.return_value = MagicMock()
    
    # Invoke the method directly
    credits_window.openBedrockWebsite()

    # Assert that subprocess.Popen was called with the correct command
    mock_popen.assert_called_once_with(['xdg-open', 'https://bedrocklinux.org/'])

@patch('subprocess.Popen')
def test_open_repo(mock_popen, credits_window):
    # Mock Popen so that no external commands are run
    mock_popen.return_value = MagicMock()

    # Invoke the method directly
    credits_window.openRepo()

    # Assert that subprocess.Popen was called with the correct command
    mock_popen.assert_called_once_with(['xdg-open', 'https://github.com/stratos-linux'])