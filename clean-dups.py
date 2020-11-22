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

HELP_MESSAGE = "./clean-dups.py <path> [DELETE]"

def main(argv):
    thePath = argv[1]
    send_to_trash = False
    if len(argv) == 3:
        if argv[2] != 'DELETE':
            print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
            sys.exit(1)
        else:
            send_to_trash = True
    print(f"Path to cleanup: {thePath}\n")
    if not path.isdir(thePath):
        print(f"ERROR: Path must be a valid directory")
        sys.exit(1)

    for filename in glob.iglob(thePath + '/**/*', recursive=True):
        if not path.isdir(filename):
            filename_prefix, extension = path.splitext(filename)
            if re.search(r"-\d$", filename_prefix) is not None:
                if send_to_trash:
                    print("Sending to trash: {} with extension {}".format(filename_prefix, extension))
                    send2trash(filename)
                else:
                    print("Candidate file for trash: {} with extension {}".format(filename_prefix, extension))

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    main(sys.argv)
    sys.exit(0)
