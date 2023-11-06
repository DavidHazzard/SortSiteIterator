# SortSiteIterator

Hello! This tool came out of a need to run multiple SortSite scans for separate domains iteratively. The goal was to save the time between a scan finishing, a user realizing it was done, exporting the necessary information and starting the next scan.

The app takes up to two files:
1. A sites file (syntax below)
2. An .sset config file

The app allows a user to 
1. ..toggle robots.txt compliance (which will override the config file)
1. ..toggle between the trial/full versions
2. ..specify the scan scope for the requested scans
3. ..view the scan progress in real time

For the app to run on earlier versions of SortSite, the full path to the SortSiteCmd.exe file will need to be provided.
