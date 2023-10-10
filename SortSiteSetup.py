import os
import datetime
import sys
import SiteInfo

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

## Class Declarations
class SortSiteSetup:

    def __init__(self, sitesFile, settingsFile, obeyRobots, isTrial, programLocation, scope):
        self.sitesFile = self.strip_sites(sitesFile)
        self.settingsFile = self.get_settings_path(settingsFile)
        self.obeyRobots = obeyRobots
        self.isTrial = isTrial
        self.programLocation = self.get_program_location(programLocation, isTrial)
        self.scope = scope if scope != None else defaultScope
        self.scan_directory = None

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


    def create_config_file(self, siteInfo: SiteInfo):
        scan_directory = self.get_directory('_scans', siteInfo)
        self.scan_directory = scan_directory
        
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
            sys.stdout.write(f'\n Created directory: \n {config_directory}')
        
        if os.path.exists(scan_directory) == False:
            os.makedirs(scan_directory)
            sys.stdout.write(f'Created directory: \n {scan_directory}')
        
        if os.path.exists(filePath) == False:
            with open(filePath, 'w') as f:
                f.write(ssconfig)
                sys.stdout.write(f'Created config file: \n {filePath} \n')
        else:
            sys.stdout.write(f'Config file already exists: \n {filePath} \n')

        return filePath.replace('/', '\\')
    
    def get_directory(self, path_text: str, siteInfo: SiteInfo):
        robots = 'obey_robots' if self.obeyRobots else 'ignore_robots'
        directory_part = f'/{monthYear}/{self.scope}_{robots}/{siteInfo.siteSubdomain}/'
        
        return f'{baseDirectory}{siteInfo.clientShortName}{path_text}{directory_part}'