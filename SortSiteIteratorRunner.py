import subprocess
from SiteInfo import SiteInfo
from SortSiteSetup import SortSiteSetup
from PyQt5.QtCore import QObject, pyqtSignal


class SortSiteIteratorRunner(QObject):
    commandLineOutput = pyqtSignal(str)

    def __init__(self, src: SortSiteSetup):
        super().__init__()
        self.src = src
    
    def run(self):
        progress = 0
        for site in self.src.sitesFile:
            siteInfo = SiteInfo.from_site_str(site)
            if siteInfo is not None:
                configFile = self.src.create_config_file(siteInfo)
                self.commandLineOutput.emit(f'Running SortSite scan for {siteInfo.siteName}...')
                process = subprocess.Popen([self.src.programLocation, configFile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while True:
                    output = process.stdout.readline().decode()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.commandLineOutput.emit(output)
                self.commandLineOutput.emit(f"Scan for {siteInfo.siteName} complete. \n The results can be found in {self.src.scan_directory} \n")
                progress = progress + ((1 / len(self.src.sitesFile)) * 100)
                self.commandLineOutput.emit(f"{progress}\n")
        self.commandLineOutput.emit('Finished')