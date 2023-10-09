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
	<ProcessURL>{site}</ProcessURL>		
	<Scope>{scope}</Scope>
    <UseRobotsTxt>{use_robots}</UseRobotsTxt>
	<SettingsFile>{settingsFile}</SettingsFile>
	<ReportOutputPath>{scan_directory}</ReportOutputPath>
    </Site>
"""
defaultScope = 'scopeSite'
progress = 0

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
    def __init__(self, sitesFile, settingsFile, obeyRobots, isTrial, programLocation, scope):
        self.sitesFile = self.strip_sites(sitesFile)
        self.settingsFile = self.get_settings_path(settingsFile)
        self.obeyRobots = obeyRobots
        self.isTrial = isTrial
        self.programLocation = self.get_program_location(programLocation, isTrial)
        self.scope = scope if scope != None else defaultScope

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
    
    def get_program_location(self, customProgramLocation: str, isTrial: bool):
        if customProgramLocation == None:
            if isTrial == True:
                return 'C:\Program Files (x86)\PowerMapper Software\SortSite 6 Trial\SortSiteCmd.exe'
            else:
                return 'C:\Program Files (x86)\PowerMapper Software\SortSite 6\SortSiteCmd.exe'
        else:
            return customProgramLocation          

    def run(self):
        for site in self.sitesFile:
            siteInfo = SiteInfo.from_site_str(site)
            if siteInfo is not None:
                configFile = self.create_config_file(siteInfo)
                print(f'Running SortSite scan for {siteInfo.siteName}...')
                print(self.programLocation)
                subprocess.run([self.programLocation, configFile], check=True)
                print(f"Scan for {siteInfo.siteName} complete. \n The results can be found in {scan_directory} \n")
                progress = progress + ((1 / len(self.sitesFile)) * 100)
                sys.stdout.write(f"{progress}\n")

    def create_config_file(self, siteInfo: SiteInfo):
        global scan_directory
        scan_directory = self.get_directory('_scans', siteInfo)
        config_directory = self.get_directory('_configs', siteInfo)

        filePath = f'{config_directory}{siteInfo.siteSubdomain}.ssconfig'
        
        ssconfig = ssconfigTemplate.format(
            site=siteInfo.siteName, 
            scope=self.scope,
            use_robots=self.obeyRobots,
            settingsFile=self.settingsFile, 
            scan_directory=scan_directory
        )

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
    
    def get_directory(self, path_text: str, siteInfo: SiteInfo):
        directory_part = f'/{monthYear}/{self.scope}/{siteInfo.siteSubdomain}/'

        if self.obeyRobots:
            directory_part = f'{directory_part}obey_robots/'
        else:
            directory_part = f'{directory_part}ignore_robots/'
        
        return f'{baseDirectory}{siteInfo.clientShortName}{path_text}{directory_part}'