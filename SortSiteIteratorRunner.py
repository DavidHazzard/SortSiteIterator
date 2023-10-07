import subprocess
import os
import datetime
import sys
import ast

## var declarations
userLogin = os.getlogin()
baseDirectory = f'C:/Users/{userLogin}/Documents/SortSiteScans/'
monthYear = datetime.datetime.now().strftime('%b%Y')
ssconfigTemplate = """
    <Site>
	<!-- scan this URL -->
	<ProcessURL>{site}</ProcessURL>		

	<Scope>scopeSite</Scope>

    <UseRobotsTxt>false</UseRobotsTxt>

	<SettingsFile>{settingsFile}</SettingsFile>

	<!-- save results in this directory - must have a trailing slash -->
	<ReportOutputPath>{scan_directory}</ReportOutputPath>

    </Site>
"""

## Class Declarations
class SiteInfo:
    def __init__(self, siteName, siteSubdomain, clientShortName):
        self.siteName = siteName
        self.siteSubdomain = siteSubdomain
        self.clientShortName = clientShortName

    @classmethod
    def from_site_str(cls, site_str: str):
        siteDict = ast.literal_eval(site_str)
        if isinstance(siteDict, dict):
            clientShortName = list(siteDict.keys())[0]
            siteName = siteDict[clientShortName][0]
            siteSubdomain = siteDict[clientShortName][1]
            return SiteInfo(siteName, siteSubdomain, clientShortName)
        else:
            print(f"Error parsing str => dictionary: {site_str}")
            return None

class SortSiteRunner:
    def __init__(self, sitesFile, settingsFile):
        self.sitesFile = self.strip_sites(sitesFile)
        self.settingsFile = self.get_settings_path(settingsFile)
    
    def strip_sites(self, sitesFile):
        with open(sitesFile, 'r') as f:
            sitesList = [line.strip() for line in f 
                        if line.strip()]
        return sitesList
    
    def get_settings_path(self, settingsFile):
        if settingsFile == 'None':
            app_path = os.path.abspath('.')
            return os.path.join(app_path, 'baseConfig.sset')
        else:
            return f'{settingsFile}'
    
    def run(self):
        for site in self.sitesFile:
            siteInfo = SiteInfo.from_site_str(site)
            if siteInfo is not None:
                configFile = self.create_config_file(siteInfo)
                print(f'Running SortSite scan for {siteInfo.siteName}...')
                subprocess.run(["C:\Program Files (x86)\PowerMapper Software\SortSite 6\SortSiteCmd.exe", configFile], check=True)
                print(f"Scan for {siteInfo.siteName} complete. \n The results can be found in {scan_directory} \n")
                progress = progress + ((1 / len(self.sitesFile)) * 100)
                sys.stdout.write(f"{progress}\n")

    def create_config_file(self, siteInfo: SiteInfo):
        global scan_directory
        scan_directory = f'{baseDirectory}{siteInfo.clientShortName}_scans/{monthYear}/{siteInfo.siteSubdomain}/'
        config_directory = f'{baseDirectory}{siteInfo.clientShortName}_configs/{monthYear}/'
        filePath = f'{config_directory}{siteInfo.siteSubdomain}.ssconfig'
        
        ssconfig = ssconfigTemplate.format(site=siteInfo.siteName, settingsFile=self.settingsFile, scan_directory=scan_directory)

        if os.path.exists(config_directory) == False:
            os.makedirs(config_directory)
            print(f'\n Created directory: \n {config_directory}')
        
        if os.path.exists(scan_directory) == False:
            os.makedirs(scan_directory)
            print(f'Created directory: \n {scan_directory}')
        
        if os.path.exists(filePath) == False:
            with open(filePath, 'w') as f:
                f.write(ssconfig)
                print(f'Created config file: \n {filePath} \n')
        else:
            print(f'Config file already exists: \n {filePath} \n')

        return filePath.replace('/', '\\')