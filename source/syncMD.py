#!/bin/env python3

# This synchronizes existing *.md files in the
# github repo with sphinx documentation in
# this source directory.

# This script uses the m2r2 script to convert
# MD files to RST files.

# (-c) check
#   * Checks for updates and possible collisions.
# (-u) update
#   * Checks timestamps between *.md and *.rst files
#     and performs updates.
# (-u) (-a) update (--all)
#   * This updates all *.rst files using available *.md
#     files regardless of timestamp.

import os, sys, argparse
from gridtools import sysinfo

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--all", action="store_true",
        help="Update everything")
parser.add_argument("-u", "--update", action="store_true",
        help="Update only newer files")
parser.add_argument("-c", "--check", action="store_true",
        help="Check and show files that would be updated")
args = parser.parse_args()

# Set argument values
checkFlag = args.check
updateFlag = args.update
allFlag = args.all

# For now, this script will assume that we are in
# the ~git/gridtools/source directory when we
# run the script.  We need to go back one
# directory and begin a nested scan of *.md files.

def walkDirectory(dirName):
    # os.walk does automatic recursion
    for root, dirs, files in os.walk(dirName, topdown=False, followlinks=False):
        if len(root) > 7 and root[0:8] == "./source":
            continue
        for name in files:
            fname, fext = os.path.splitext(os.path.join(root, name))
            if fext == ".md":
                print('FILE:', os.path.join(root, name))

os.chdir("..")
# Make sure we see the anticipated directories.
mustScanDirectories = [
    'conda', 'docs', 'examples', 'gridtools', 'tests'
]

for dirName in mustScanDirectories:
    if not(os.path.isdir(dirName)):
        sys.exit("ERROR: We do not seem to be in our source tree!")

walkDirectory(".")
