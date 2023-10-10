import sys
import ast

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
            sys.stderr.write(f"Error parsing str => dictionary: {site_str}")
            return None