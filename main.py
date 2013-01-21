from fiona_ogr import getIntersections

__author__ = 'spousty'

import os
import logging

'''
Steps
1) Read in the one file with the geometry we want to use to select or clip the others
2) Bring in the list of all the shapefiles in the directory to be processed
3) Select or clip each one
4) Then Project it
5) Save it to disk
6) if it is a point file save it to JSON to import into MongoDB (this will also be a nice shape -> mongo script)
6) Write a SQL file (using OGR/Fiona)

'''

logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
#logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

def main():
    #clipDir = '/home/spousty/Dropbox/Redhat_OS/Work/SCCGeo/_clip'
    clipDir = '/Users/spousty/Dropbox/Redhat_OS/Work/SCCGeo/_clip'
    #toBeClippedDir = '/home/spousty/Dropbox/Redhat_OS/Work/SCCGeo/ToBeClipped'
    toBeClippedDir = '/Users/spousty/Dropbox/Redhat_OS/Work/SCCGeo/ToBeClipped'
    #outputDir =  '/home/spousty/Dropbox/Redhat_OS/Work/SCCGeo/clipped'
    outputDir =  '/Users/spousty/Dropbox/Redhat_OS/Work/SCCGeo/clipped'

    clipFile = ""
    filesToBeClipped = []

    #Get the single file in read mode. We need the file ending .shp
    fileListing = os.listdir(clipDir)
    for f in fileListing:
        if f.endswith(".shp"):
            clipFile = clipDir + '/' +  f

    #now walk the tree and get every shapefile listed in the subdirs
    for root, dirs, files in os.walk(toBeClippedDir):
        for f in files:
            if f.endswith(".shp"):
                filesToBeClipped.append( root + '/' + f)

    #alright now we have all our files we need time to do geospatial work

    for toBeClipped in filesToBeClipped:

        getIntersections(clipFile, toBeClipped, outputDir)



    print "\n *** done ***"

if __name__ == "__main__":
    main()