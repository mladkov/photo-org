#!/usr/bin/env python3

# Tested with Python 3.8 or above

import sys
import glob
import os
from os import path
import exifread
import shutil
import subprocess
import hashlib
from send2trash import send2trash
import re

HELP_MESSAGE = "./zap-model.py <path> {NIKONZ6|NIKONZ6_2} [--nocheck]"

camera_model_map = { "NIKONZ6_2": "NIKON Z 6_2", 
                     "NIKONZ6"  : "NIKON Z 6"
                   }

def exif_matches_model(filename, camera_model):
    # Use exiftool to see what the current camera model is
    #print(f"Checking {filename} matches {camera_model}")
    exiftool_res = subprocess.run([r'c:\Users\Family\Downloads\exiftool-12.05\exiftool.exe',
                        '-model', filename], stdout=subprocess.PIPE, encoding='UTF-8')
    for line in exiftool_res.stdout.splitlines():
        model_exif = line[34:].replace('"', '').strip()
        print(f"EXIF MODEL: {model_exif}, looking to update to {camera_model}")
        break
    return model_exif == camera_model

def exif_camera_model_update(filename, camera_model):
    # Use exiftool to replace the model as provided by overriding the
    # current file as well
    failed_update = False
    exiftool_res = subprocess.run([r'c:\Users\Family\Downloads\exiftool-12.05\exiftool.exe',
                        '-overwrite_original', '-model="{}"'.format(camera_model), filename], stdout=subprocess.PIPE, encoding='UTF-8')
    for line in exiftool_res.stdout.splitlines():
        if line.strip() != '1 image files updated':
            failed_update = True
            print(line)
        else:
            break
    if failed_update:
        raise ProcessLookupError(f"Unable to process {filename} with model {camera_model}")

        
def main(argv):
    thePath = argv[1]
    camera_model = camera_model_map.get(argv[2])
    nocheck_flag = False
    if len(argv) == 4 and argv[3] == '--nocheck':
        nocheck_flag = True
        print("No check flag detected - will simply update without checking model of existing file")
    if camera_model is None:
        print(f"Camera model {argv[2]} not yet supported!")
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    print(f"Path to zap with model '{camera_model}': {thePath}\n")
    if not path.isdir(thePath):
        print(f"ERROR: Path must be a valid directory")
        sys.exit(1)
    for filename in glob.iglob(thePath + '/**/*', recursive=True):
        if not path.isdir(filename):
            filename_prefix, extension = path.splitext(filename)
            if extension == ".NEF":
                print(f"filename: {filename}, with extension: {extension}")
                # Find out whether it is already set to the model
                # we're intending to set it to
                if nocheck_flag or not exif_matches_model(filename, camera_model):
                    print(f"UPDATING file: {filename} with model '{camera_model}'")
                    exif_camera_model_update(filename, camera_model)
                
if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    main(sys.argv)
    sys.exit(0)
