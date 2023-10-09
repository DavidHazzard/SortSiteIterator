import os
import shutil
from SortSiteIteratorRunner import SortSiteRunner

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

class SortSiteIteratorAppShell(QMainWindow):
    def __init__(self):
        super().__init__()    
        self.setFont(QFont('Source Sans Pro', 16))

        self.createFileSelectObject(
                'Sites',
                'sitesField',
                "Select a file containing a list of sites to scan, one per line, no commas delimiting them.\nThe contents of the file should be formatted as follows:\n { Client Shortname , ['Site Url', 'intended file name' ]\n i.e. { 'WK', ['https://www.wolterskluwer.com', 'wolterskluwer'] }"
            )
        self.createFileSelectObject(
                'Config', 
                'configField',
                "Select a file containing the SortSite6 compliant settings you wish to use for the scan.\nIf you do not select a file, the default config defined in ./SortSiteScans/baseConfig.sset will be used."
            )
        self.createFileSelectObject(
                'SortSite Command Application', 
                'programLocation', 
                'Select the SortSiteCmd.exe file in the SortSite 6 installation directory'
            )
        self.programLocationWidget.setEnabled(False)
        self.programLocationButtonWidget.setEnabled(False)

        self.obeyRobotsCheckBox = QCheckBox('Obey Robots.txt', self)
        self.obeyRobotsCheckBox.setChecked(True)
        self.obeyRobotsCheckBox.setObjectName('obeyRobotsCheckBox')

        self.isTrialCheckBox = QCheckBox('Trial Version', self)
        self.isTrialCheckBox.setChecked(False)
        self.isTrialCheckBox.setObjectName('isTrialCheckBox')

        self.usingCustomProgramPath = False
        self.programInDefaultInstallLocationCheckBox = QCheckBox('Is SortSite installed in the default location?', self)
        self.programInDefaultInstallLocationCheckBox.setChecked(True)
        self.programInDefaultInstallLocationCheckBox.setObjectName('programInCustomInstallLocationCheckBox')
        self.programInDefaultInstallLocationCheckBox.stateChanged.connect(self.toggleProgramInCustomInstallLocation)

        self.scopeDropdown = QComboBox(self)
        self.scopeDropdown.addItem('Entire Site', 'scopeSite')
        self.scopeDropdown.addItem('Current Page', 'scopePage')
        self.scopeDropdown.addItem('Current Page and Links', 'scopePageAndLinks')        

        self.statusLabel = QLabel('Ready', self)
        self.statusLabel.setObjectName('statusLabel')

        self.runButton = QPushButton('Run', self)
        self.runButton.clicked.connect(self.runSortSite)
        self.runButton.setObjectName('runButton')

        self.cancelButton = QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.cancelSortSite)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setObjectName('cancelButton')

        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet('QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: white; width: 70%; content-align: center, padding: 10px; } QProgressBar::chunk { background-color: #0078d7; }')
        self.progressBar.move(0, 0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setObjectName('progressBar')

        self.activityPanel = QTextEdit(self)
        self.activityPanel.setReadOnly(True)
        self.activityPanel.setFont(QFont('Courier New', 10))
        self.activityPanel.setObjectName('activityPanel')
    
        vbox = QVBoxLayout()
        vbox.addWidget(self.sitesFieldLabel)
        vbox.addLayout(self.sitesFieldLayout)
        vbox.addWidget(self.configFieldLabel)
        vbox.addLayout(self.configFieldLayout)
        vbox.addWidget(self.programLocationLabel)
        vbox.addLayout(self.programLocationLayout)
        vbox.addWidget(self.obeyRobotsCheckBox)
        vbox.addWidget(self.isTrialCheckBox)
        vbox.addWidget(self.programInDefaultInstallLocationCheckBox)
        vbox.addWidget(self.scopeDropdown)
        vbox.addWidget(self.statusLabel)
        vbox.addWidget(self.progressBar)
        vbox.addWidget(self.activityPanel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.runButton)
        hbox.addWidget(self.cancelButton)
        vbox.addLayout(hbox)

        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        centralWidget.setObjectName('centralWidget')
        self.setCentralWidget(centralWidget)

        self.setWindowTitle('SortSite Iterator V1')
        self.setStyleSheet('''
            QMainWindow {
                font-size: 16px;
                font-weight: bold;
                content-align: center;
            }
            QPushButton {  
                background-color: #0078d7;
                border: 2px solid #0078d7;
                border-radius: 5px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0063b1;
                border: 2px solid
            }
            QPushButton:disabled {
                background-color: #9FC5E7;
                border: 2px solid #9FC5E7;
                border-radius: 5px;
            }
            #statusLabel {
                font-size: 24px;
            }
            #activityPanel {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: white;
                width: 70%;
                height: 200px;
                content-align: center;
                padding: 10px;
            }
            QLineEdit {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: white;
                width: 70%;
                content-align: center;
                padding: 10px;
            }
            QLineEdit:disabled {
                background-color: #f0f0f0;
            }         
            QLabel:disabled {
                color: #a9a9a9;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: white;
                width: 70%;
                content-align: center;
                padding: 10px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
            }
            QComboBox {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: white;
                width: 30%;
                content-align: center;
                padding: 10px;
            }                            
        ''')

        self.show()

    def toggleProgramInCustomInstallLocation(self):
        isCustomProgramLocation = not self.programInDefaultInstallLocationCheckBox.isChecked()
        self.programLocationWidget.setEnabled(isCustomProgramLocation)
        self.programLocationButtonWidget.setEnabled(isCustomProgramLocation)

    def updateProgressBar(self, progress):
        self.progressBar.setValue(int(progress))

    def createFileSelectObject(self, inputLabel, inputFieldName, tooltipText):
        inputLabelWidget = QLabel(f'{inputLabel} file:', self)
        inputLabelWidget.setObjectName(f'{inputFieldName}Label')

        inputFieldWidget = QLineEdit(self)
        inputFieldWidget.setObjectName(f'{inputFieldName}Field')
        
        inputButtonWidget = QPushButton('Select', self)
        inputButtonWidget.setToolTip(tooltipText)
        inputButtonWidget.clicked.connect(lambda: self.selectFile(inputLabel, inputFieldName))
        inputButtonWidget.setObjectName(f'{inputFieldName}Button')

        inputLayout = QHBoxLayout()
        inputLayout.addWidget(inputFieldWidget)
        inputLayout.addWidget(inputButtonWidget)

        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(20)

        setattr(self, f'{inputFieldName}Label', inputLabelWidget)
        setattr(self, f'{inputFieldName}Layout', inputLayout)
        setattr(self, f'{inputFieldName}Widget', inputFieldWidget)
        setattr(self, f'{inputFieldName}ButtonWidget', inputButtonWidget)

        return inputLayout

    def selectFile(self, fileType, inputFieldName):
        inputFieldWidget = getattr(self, f'{inputFieldName}Widget')  # Get attribute from self object
        fileName, _ = QFileDialog.getOpenFileName(self, f'Select {fileType} File')
        if fileName:
            inputFieldWidget.setText(fileName)

    def runSortSite(self):
        if self.inputIsValid() == False:
            return

        self.statusLabel.setText('Running...')
        self.cancelButton.setEnabled(True)
        self.runButton.setEnabled(False)

        self.thread = SortSiteIteratorThread(
            self.sitesFieldWidget.text()
            ,self.configFieldWidget.text()
            ,self.obeyRobotsCheckBox.isChecked()
            ,self.isTrialCheckBox.isChecked()
            ,self.programLocationWidget.text()
                if self.programInDefaultInstallLocationCheckBox.isChecked() == False 
                else None
            ,self.scopeDropdown.currentData()
        )
        self.thread.outputReceived.connect(self.handleOutputReceived)
        self.thread.progressUpdated.connect(self.updateProgressBar)
        self.thread.finished.connect(self.handleThreadFinished)
        self.thread.start()

    def inputIsValid(self):
        not_exists_text = 'No file exists at the provided location. Please select a {type} file.'

        if self.sitesFieldWidget.text() == '':
            self.statusLabel.setText('Please select a sites file.')
            self.statusLabel.setStyleSheet('color: red')
            return False
        elif self.sitesFieldWidget.text() != '' and not os.path.isfile(self.sitesFieldWidget.text()):
            self.statusLabel.setText(not_exists_text.format(type='sites'))
            self.statusLabel.setStyleSheet('color: red')
            return False
        elif self.configFieldWidget.text() != '' and not os.path.isfile(self.configFieldWidget.text()):
            self.statusLabel.setText(not_exists_text.format(type='config'))
            self.statusLabel.setStyleSheet('color: red')
            return False
        elif self.programInDefaultInstallLocationCheckBox.isChecked() == False and self.programLocationWidget.text() == '':
            self.statusLabel.setText('Please select a SortSiteCmd.exe executable')
            self.statusLabel.setStyleSheet('color: red')
            return False
        elif self.programInDefaultInstallLocationCheckBox.isChecked() == False and not os.path.exists(self.programLocationWidget.text()):
            self.statusLabel.setText(not_exists_text.format(type='SortSiteCmd.exe executable'))
            self.statusLabel.setStyleSheet('color: red')
            return False
        else:
            self.statusLabel.setText('Ready')
            self.statusLabel.setStyleSheet('color: black')
            return True

    def handleOutputReceived(self, output):
        logFile = open('log.txt', 'a')
        try:
            float(output.strip())
            output = f'{float(output.strip()):.2f}% complete'
        except ValueError:
            pass
        logFile.write(output)
        logFile.close()
        self.activityPanel.append(output.strip())

    def handleThreadFinished(self):
        self.statusLabel.setText('Finished')
        self.cancelButton.setEnabled(False)
        self.runButton.setEnabled(True)

    def cancelSortSite(self):
        self.thread.terminate()
        self.statusLabel.setText('Cancelled')
        self.cancelButton.setEnabled(False)
        self.runButton.setEnabled(True)

class SortSiteIteratorThread(QThread):
    outputReceived = pyqtSignal(str)
    progressUpdated = pyqtSignal(float)
    cancelled = pyqtSignal()

    def __init__(self, sitesFile, configFile, obeyRobots: bool, isTrial: bool, programLocation: str, scope: str):
        super().__init__()
        self.sitesFile = sitesFile
        self.configFile = configFile
        self.obeyRobots = obeyRobots
        self.isTrial = isTrial
        self.programLocation = programLocation
        self.scope = scope

    def run(self):
        runner = SortSiteRunner(
            self.sitesFile, 
            self.configFile, 
            self.obeyRobots, 
            self.isTrial, 
            self.programLocation, 
            self.scope
        )
        print(self.isTrial)
        process = runner.run()

        while True:
            output = process.sdout.readline().decode() 
            if output == '' and process.poll() is not None:
                break
            if output:
                self.outputReceived.emit(output)
                try:
                    progress = float(output.strip())
                    self.progressUpdated.emit(progress)
                except ValueError:
                    pass
        
        process.wait()
        self.progressUpdated.emit(100)