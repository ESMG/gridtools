#!/bin/env python3

# This synchronizes existing *.md files in the
# github repo with sphinx documentation in
# this source directory.

# This script uses the m2r2 script to convert
# MD files to RST files.

# check
#   * Checks for updates and possible collisions.
# update
#   * Checks timestamps between *.md and *.rst files
#     and performs updates.
# update --all
#   * This updates all *.rst files using available *.md
#     files regardless of timestamp.
