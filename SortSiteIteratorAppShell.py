import os
import shutil
from SortSiteIteratorRunner import SortSiteRunner

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

class SortSiteIteratorAppShell(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createFileSelectObject('Sites',
                                    'sitesField',
                                    "Select a file containing a list of sites to scan, one per line, no commas delimiting them.\nThe contents of the file should be formatted as follows:\n { Client Shortname , ['Site Url', 'intended file name' ]\n i.e. { 'WK', ['https://www.wolterskluwer.com', 'wolterskluwer'] }")
        self.createFileSelectObject('Config', 
                                    'configField',
                                    "Select a file containing the SortSite6 compliant settings you wish to use for the scan.\nIf you do not select a file, the default config defined in ./SortSiteScans/baseConfig.sset will be used.")

        self.statusLabel = QLabel('Ready', self)

        self.runButton = QPushButton('Run', self)
        self.runButton.clicked.connect(self.runSortSite)

        self.cancelButton = QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.cancelSortSite)
        self.cancelButton.setEnabled(False)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet('QProgressBar { border: 2px solid grey; border-radius: 5px; background-color: white; width: 70%; content-align: center, padding: 10px; } QProgressBar::chunk { background-color: #0078d7; }')
        self.progressBar.move(0, 0)
        self.progressBar.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addLayout(self.sitesFieldLayout)
        vbox.addLayout(self.configFieldLayout)
        vbox.addWidget(self.statusLabel)
        vbox.addWidget(self.progressBar)

        self.activityPanel = QTextEdit(self)
        self.activityPanel.setReadOnly(True)
        self.activityPanel.setFont(QFont('Courier New', 10))
        vbox.addWidget(self.activityPanel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.runButton)
        hbox.addWidget(self.cancelButton)
        vbox.addLayout(hbox)

        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)

        self.setWindowTitle('SortSite Iterator V1')
        self.setStyleSheet('font-size: 14px; font-family: Arial;')

        self.show()

    def updateProgressBar(self, progress):
        self.progressBar.setValue(int(progress))

    def createFileSelectObject(self, inputLabel, inputFieldName, tooltipText):
        inputLabelWidget = QLabel(f'{inputLabel} file:', self)
        inputFieldWidget = QLineEdit(self)
        inputButtonWidget = QPushButton('Select', self)
        inputButtonWidget.setToolTip(tooltipText)
        inputButtonWidget.clicked.connect(lambda: self.selectFile(inputLabel, inputFieldName))

        inputLayout = QHBoxLayout()
        inputLayout.addWidget(inputLabelWidget)
        inputLayout.addWidget(inputFieldWidget)
        inputLayout.addWidget(inputButtonWidget)

        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(20)

        setattr(self, f'{inputFieldName}Layout', inputLayout)
        setattr(self, f'{inputFieldName}Widget', inputFieldWidget)
        setattr(self, f'{inputFieldName}ButtonWidget', inputButtonWidget)

        return inputLayout

    def downloadFile(self, filePath):
        downloadPath, _ = QFileDialog.getSaveFileName(self, 'Save File', os.path.basename(filePath))
        if downloadPath:
            shutil.copyfile(filePath, downloadPath)

    def selectFile(self, fileType, inputFieldName):
        inputFieldWidget = getattr(self, f'{inputFieldName}Widget')  # Get attribute from self object
        fileName, _ = QFileDialog.getOpenFileName(self, f'Select {fileType} File')
        if fileName:
            inputFieldWidget.setText(fileName)

    def runSortSite(self):
        sitesFile = self.sitesFieldWidget.text()
        configFile = self.configFieldWidget.text()

        self.statusLabel.setText('Running...')
        self.cancelButton.setEnabled(True)
        self.runButton.setEnabled(False)

        self.thread = SortSiteIteratorThread(sitesFile, configFile)
        self.thread.outputReceived.connect(self.handleOutputReceived)
        self.thread.progressUpdated.connect(self.updateProgressBar)
        self.thread.finished.connect(self.handleThreadFinished)
        self.thread.start()

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

    def __init__(self, sitesFile, configFile):
        super().__init__()
        self.sitesFile = sitesFile
        self.configFile = configFile

    def run(self):
        runner = SortSiteRunner(self.sitesFile, self.configFile)
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