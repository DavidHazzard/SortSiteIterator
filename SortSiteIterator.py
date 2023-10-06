import subprocess
import time
import os
import datetime
import sys
import ast

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

## Helper Methods/Var Declarations and Definitions
def get_login():
    if supplied_user_exists():
        return sys.argv[2]
    else:
        return os.getlogin()

def supplied_user_exists():
    return len(sys.argv) > 3 and sys.argv[3] != 'None' and os.path.exists(f'C:/Users/{sys.argv[3]}')

userLogin = get_login()

baseDirectory = f'C:/Users/{userLogin}/Documents/SortSiteScans/'

monthYear = datetime.datetime.now().strftime('%b%Y')

sitesFile = sys.argv[1]
with open(sitesFile, 'r') as f:
    sitesList = [line.strip() for line in f 
                 if line.strip()]

def get_settings_path(settingsFile):
    if settingsFile == 'None':
        return os.path.join(sys._MEIPASS, 'baseConfig.sset')
    else:
        return f'{settingsFile}'
    
settingsFile = get_settings_path(sys.argv[2])

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

## Business Logic-y Definitions
def create_config_file(siteInfo: SiteInfo):
    global scan_directory
    scan_directory = f'{baseDirectory}{siteInfo.clientShortName}_scans/{monthYear}/{siteInfo.siteSubdomain}/'
    config_directory = f'{baseDirectory}{siteInfo.clientShortName}_configs/{monthYear}/'
    filePath = f'{config_directory}{siteInfo.siteSubdomain}.ssconfig'
    
    ssconfig = ssconfigTemplate.format(site=siteInfo.siteName, settingsFile=settingsFile, scan_directory=scan_directory)

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

## Main
progress = 0

for site in sitesList:
    print(site)
    siteInfo = SiteInfo.from_site_str(site)
    if siteInfo is not None:
        configFile = create_config_file(siteInfo)
        print(f'Running SortSite scan for {siteInfo.siteName}...')
        subprocess.run(["C:\Program Files (x86)\PowerMapper Software\SortSite 6 Trial\SortSiteCmd.exe", configFile], check=True)
        print(f"Scan for {siteInfo.siteName} complete. \n The results can be found in {scan_directory} \n")
        progress = progress + ((1 / len(sitesList)) * 100)
        sys.stdout.write(f"{progress}\n")
