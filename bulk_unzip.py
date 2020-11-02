#!/usr/bin/env python3

import sys
import glob
from os import path
import zipfile
import time

HELP_MESSAGE = "./bulk_unzip.py <source-path>"

def main(argv):
    srcPath = argv[1]
    print(f"Source Path: {srcPath}\n")

    # We loop through all files in the directory given to us.
    # We do NOT recursively go through the directory
    for filename in glob.iglob(srcPath + '/*', recursive=False):
        # The filename will be the full path like so:
        #
        # filename: G:\test\files.zip
        #
        # However, the filename_prefix and extension will be:
        #
        # filename_prefix: G:\test\files
        # extension      : .zip
        #
        # The idea is, for those files with .zip extensions, we'll call
        # the unzip utility to extract the file and place it in the
        # "filename_prefix" directory.
        # If the directory does not exist, we'll create it.
        # If it does exist, this should mean that this zip file was already
        # unzipped, in which case we'll leave it alone.
        filename_prefix, extension = path.splitext(filename)
        if extension == ".zip":
            tic = time.perf_counter()
            print("filename: {}, prefix: {}, extension: {}".format(filename, filename_prefix, extension), flush=True)
            if path.isdir(filename_prefix):
                print("  --> Skipping {} as it seems it is already unzipped in this directory".format(filename), flush=True)
            else:
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall(filename_prefix)
                    print("  --> Done extracting {} to {}".format(filename, filename_prefix), flush=True)
            toc = time.perf_counter()
            print(f"  ({toc - tic:0.4f}sec) --> ({(toc - tic)/60:0.4f}min)", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    main(sys.argv)
    sys.exit(0)