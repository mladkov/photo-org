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

HELP_MESSAGE = "./photo-org.py <source-path> <target-path>"
DEBUG_MODE = False

class ExifProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.uniq_id  = 0
    
    def process_exif(self):
        self.filename_prefix, self.extension = path.splitext(self.filename)
        if self.extension is not None and len(self.extension) != 0 and self._is_supported_extension(self.extension):
            try:
                f = open(self.filename, 'rb')
                self.tags = exifread.process_file(f, strict=True)
                # It's possible Image Model is not found when we processed the exif but the rest of
                # EXIF data is useable. In which case, let's just set the Image Model to 'unknown'
                # which becomes part of the filename.
                if self.tags.get('Image Model') is None:
                    self.tags['Image Model'] = 'unknown'
                #print(f"Tags: {self.tags}")
                if len(self.tags) == 0 or self.tags.get('EXIF DateTimeOriginal') is None:
                    # We couldn't get any EXIF data from the file, we have
                    # to resort using command line tool ExifTool instead
                    print("  WARN: Could not find any EXIF data, using ExifTool instead!")
                    exiftool_res = subprocess.run([r'c:\Users\Family\Downloads\exiftool-12.05\exiftool.exe', 
                        self.filename], stdout=subprocess.PIPE, encoding='UTF-8')
                    # Manually read through line by line to get what we need
                    for line in exiftool_res.stdout.splitlines():
                        #print(f"{line}")
                        if line.startswith('File Modification Date'):
                            # It's the Modification Date (not create/access date) that seems correct
                            # since create time is of the file when it was copied over. But modification
                            # is literally when the file was manipulated in some way, so seems the most
                            # accurate.

                            # The values are aligned by the tool, and start precisely at column 34
                            date_time = line[34:53]
                            self.tags['EXIF DateTimeOriginal'] = date_time.strip()
                f.close()
            except Exception as e:
                print("Exception processing Exif in file [{}]: {}".format(self.filename, e))
                raise e
            finally:
                if not f.closed:
                    f.close()
        else:
            raise NotImplementedError("Extension of file is not supported: {}".format(self.extension))

    def get_target_path(self, target_path):
        """Given the provided target_path, build the final target path
        with a generated sub-directory for where the input file should
        be copied
        """
        #print("  Available tags: {}".format(self.tags.keys()))
        origDtm  = self.tags["EXIF DateTimeOriginal"]
        fmtDtm   = self._format_dtm(str(origDtm))
        stdPath  = self._get_path_from_date(target_path, str(origDtm))
        model    = self.tags["Image Model"]
        fmtModel = self._format_model(str(model))
        baseFilename, extension = path.splitext(path.basename(self.filename))
        fmtBaseFilename = baseFilename.lower().replace(" ", "-")
        stdFilename = f"{fmtDtm}-{fmtModel}-{fmtBaseFilename}.jpg"
        newFilename = path.join(stdPath, stdFilename)
        if not path.isdir(stdPath):
            print(f"Creating new path: {stdPath}")
            os.makedirs(stdPath)
        return newFilename

    def get_next_uniq_target_path(self, target_path):
        self.uniq_id += 1
        orig_trg_path = self.get_target_path(target_path)
        base, ext = path.splitext(path.abspath(orig_trg_path))
        next_uniq_name = f"{base}-{self.uniq_id}{ext}"
        return next_uniq_name
        
    def _is_supported_extension(self, ext):
        if ext in ('.jpg', '.JPG', '.jpeg', '.JPEG'):
            return True
        return False

    def _format_dtm(self, orig_dtm):
        theDate, theTime = orig_dtm.split(" ")
        fmtDate = theDate.replace(":", "")
        fmtTime = theTime.replace(":", "")
        return fmtDate + "-" + fmtTime

    def _get_path_from_date(self, rootDir, origDtm):
        theDate, theTime = origDtm.split(" ")
        theYear, theMonth, theDay = theDate.split(":")
        return path.join(rootDir, theYear, theMonth, theDay)

    def _format_model(self, imageModel):
        return imageModel.lower().replace(" ", "-")

def main(argv):
    srcPath = argv[1]
    trgPath = argv[2]
    print(f"Source Path: {srcPath}\nTarget Path: {trgPath}")
    if not path.isdir(srcPath):
        print(f"ERROR: Source path must be a valid directory")
        sys.exit(1)
    if path.isdir(trgPath) == False:
        print(f"ERROR: Target path must be a valid directory")
        sys.exit(1)
    
    for filename in glob.iglob(srcPath + '/**/*', recursive=True):
        #print(f"Listing: {filename}")
        if not path.isdir(filename):
            # Only try processing items that are NOT directories (ie. files!)
            print("Found file: {}".format(filename))
            exif_proc = ExifProcessor(filename)
            exif_proc.process_exif()
            new_filename = exif_proc.get_target_path(trgPath)
            # Check if the new file name already exists
            if path.isfile(new_filename):
                #print (f"  Uh-oh, target filename already exists. Checking if checksums match")
                sha256_hash = hashlib.sha256()
                sha256_hash2 = hashlib.sha256()
                with open(filename,"rb") as f:
                    # Read and update hash string value in blocks of 4K
                    for byte_block in iter(lambda: f.read(4096),b""):
                        sha256_hash.update(byte_block)
                    #print(f"Original file: {sha256_hash.hexdigest()}")
                with open(new_filename,"rb") as f2:
                    # Read and update hash string value in blocks of 4K
                    for byte_block in iter(lambda: f2.read(4096),b""):
                        sha256_hash2.update(byte_block)
                    #print(f"New file     : {sha256_hash2.hexdigest()}")
                if sha256_hash.hexdigest() != sha256_hash2.hexdigest():
                    #print(f"  Checksums do not match, generating uniq name")
                    while path.isfile(new_filename):
                        new_filename = exif_proc.get_next_uniq_target_path(trgPath)
                    print(f"  New uniq name found: {new_filename}")
                else:
                    # Means files are identical, so instead of re-copying,
                    # we'll move it into our special Pictures trash
                    print(f"  Moving file instead to the to-be-deleted pile")
                    trash_folder = path.join(path.dirname(filename), "to-be-deleted")
                    new_filename = path.join(trash_folder, path.basename(filename))
                    if not path.isdir(trash_folder):
                        print(f"Creating trash folder: {trash_folder}")
                        os.makedirs(trash_folder)
                    print(f"  Moving to trash as file already exists: {new_filename}")
            print(f"  FROM : {filename} --> TO: {new_filename}")
            print("")
            # TODO: Trash needs to be OUTSIDE of source directory because of globbing
            #shutil.move(filename, new_filename)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{HELP_MESSAGE}  num args = {len(sys.argv)}")
        sys.exit(1)
    main(sys.argv)
    sys.exit(0)
