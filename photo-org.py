#!/usr/bin/env python3

# Needs Python 3.5 or above

import sys
import glob
import os
from os import path
import exifread
import shutil

HELP_MESSAGE = "./photo-org.py <source-path> <target-path>"
DEBUG_MODE = False

def getPathFromDate(rootDir, origDtm):
    theDate, theTime = origDtm.split(" ")
    theYear, theMonth, theDay = theDate.split(":")
    return path.join(rootDir, theYear, theMonth, theDay)

def formatDateTime(origDtm):
    theDate, theTime = origDtm.split(" ")
    fmtDate = theDate.replace(":", "")
    fmtTime = theTime.replace(":", "")
    return fmtDate + "-" + fmtTime

def formatModel(imageModel):
    return imageModel.lower().replace(" ", "-")

def main(argv):
    srcPath = argv[1]
    trgPath = argv[2]
    print(f"Source Path: {srcPath}\nTarget Path: {trgPath}")
    if path.isdir(trgPath) == False:
        print(f"Target path must be a valid directory")
        sys.exit(1)
    for filename in glob.iglob(srcPath + '**/*', recursive=True):
        fName, extension = path.splitext(filename)
        if extension is not None and len(extension) != 0 and extension in ('.jpg', '.JPG', '.jpeg', '.JPEG'):
            # Found a file - let's get the exif data from it
            f = open(filename, 'rb')
            tags = exifread.process_file(f)
            origDtm = tags["EXIF DateTimeOriginal"]
            fmtDtm = formatDateTime(str(origDtm))
            stdPath = getPathFromDate(trgPath, str(origDtm))
            model = tags["Image Model"]
            fmtModel = formatModel(str(model))
            baseFilename, extension = path.splitext(path.basename(filename))
            fmtBaseFilename = baseFilename.lower().replace(" ", "-")
            #print(f"Formatted time : {fmtDtm}")
            #print(f"Formatted model: {fmtModel}")
            #print(f"Base filename  : {fmtBaseFilename}")
            stdFilename = f"{fmtDtm}-{fmtModel}-{fmtBaseFilename}.jpg"
            newFilename = path.join(stdPath, stdFilename)
            if not path.isdir(stdPath):
                print(f"Creating new path: {stdPath}")
                os.makedirs(stdPath)
            print(f"Moving...")
            print(f"FROM : {filename}")
            print(f"TO   : {newFilename}\n")
            shutil.move(filename, newFilename)
            
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    main(sys.argv)
    sys.exit(0)
