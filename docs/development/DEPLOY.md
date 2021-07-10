<!-- DEPLOYMENT TEMPLATE -->

# Release X.Y.Z

## Previous Release

Tag: X.Y.Z `commit_hash`

This document the steps needed for a complete release.  Copy to
release folder as X.Y.Z.md and fill out.

# Checklist

 - [ ] Operating system checks
        - [ ] `x86_64`: Ubuntu 20.04.2 LTS (64 GB)
        - [ ] `x86_64`: Ubuntu 20.04.2 LTS (12 GB VM)
        - [ ] `aarch64`: Raspberry Pi 4 (8 GB)
        - [ ] `x86_64`: triton node (64 GB)
        - [ ] `x86_64`: chinook node (128 GB)
 - [ ] Verify operation of example notebooks
 - [ ] Verify operation of example scripts
 - [ ] Resync environments
   - [ ] Pip requirements.txt should closely mirror gridTools.yml
   - [ ] Update any special needs in requirements.txt
   - [ ] Resync `gridTools_export-linux-64.yml` without pip modules
   - [ ] Resync `gridTools_export-linux-64-RTD.yml` without nodejs and pip modules
   - [ ] Ensure `binder/environment.yml` is in sync
         with `conda/gridTools_export-linux-64.yml`
 - [ ] Ensure release/version is properly updated in `gridtools/__init__.py`
 - [ ] Modify any test CI Github Actions
 - [ ] Update any tests performed by pytest
 - [ ] Update TODOs.md
 - [ ] After submission of PR
   - [ ] Review commit as necessary
   - [ ] Verify CI/Actions pass
   - [ ] Verify Read the Docs render correctly
   - [ ] Verify mybinder.org is functional
 - [ ] Merge "Release x.y.z" to main
   - [ ] Reverify mybinder.org operation
   - [ ] Ensure CI/Actions continue to pass
   - [ ] Ensure ReadtheDocs renders correctly
   - [ ] Ensure MDs on github renders correctly
 - [ ] Add and commit a tag with x.y.z
 - [ ] Run through a Release on the github site
 - [ ] Place a release notice on the MOM6 forum

# General Release Notes

# Bug Fixes
