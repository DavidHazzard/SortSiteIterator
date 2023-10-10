from SortSiteSetup import SortSiteSetup
from SortSiteIteratorRunner import SortSiteIteratorRunner
from PyQt5.QtCore import QThread, pyqtSignal

class SortSiteIteratorThread(QThread):
    outputReceived = pyqtSignal(str)
    progressUpdated = pyqtSignal(float)
    cancelled = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, sitesFile, configFile, obeyRobots: bool, isTrial: bool, programLocation: str, scope: str):
        super().__init__()
        self.sitesFile = sitesFile
        self.configFile = configFile
        self.obeyRobots = obeyRobots
        self.isTrial = isTrial
        self.programLocation = programLocation
        self.scope = scope

    def run(self):
        setup = SortSiteSetup(
            self.sitesFile, 
            self.configFile, 
            self.obeyRobots, 
            self.isTrial, 
            self.programLocation, 
            self.scope
        )
        runner = SortSiteIteratorRunner(setup)
        runner.commandLineOutput.connect(self.handleCommandLineOutput)
        runner.run()

    def handleCommandLineOutput(self, output):
            if output == 'Finished':
                self.finished.emit()         
                self.progressUpdated.emit(100)
                return
            if output == 'Cancelled':
                self.cancelled.emit()
                return
            if output:
                self.outputReceived.emit(output)
                try:
                    progress = float(output.strip())
                    self.progressUpdated.emit(progress)
                except ValueError:
                    pass