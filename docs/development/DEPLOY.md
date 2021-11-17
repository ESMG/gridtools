<!-- DEPLOYMENT TEMPLATE -->

# Release X.Y.Z

## Previous Release

Tag: X.Y.Z `commit_hash`

<!--
This documents the steps needed for a complete release.  Copy to
release folder as X.Y.Z.md and fill out.  Delete these instructions
and the DEPLOYMENT TEMPLATE header above.
-->

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
 - [ ] Modify any test CI GitHub Actions
 - [ ] Update any tests performed by pytest
 - [ ] Update TODOs.md, archiving completed TODOs and milestones
 - [ ] Add contributors in their own section below for contributions via the pull request or related issues
 - [ ] After submission of PR to main
   - [ ] Review commit as necessary
   - [ ] Verify CI/Actions pass
   - [ ] Verify Read the Docs render correctly
   - [ ] Verify mybinder.org is functional
   - [ ] Review, update and/or close any issues
 - [ ] Merge "Release x.y.z" to main
   - [ ] Reverify mybinder.org operation
   - [ ] Ensure CI/Actions continue to pass (requires manual request)
   - [ ] Check CI/Actions Artifacts for proper results
   - [ ] Ensure MDs on GitHub renders correctly
 - [ ] Add and commit a tag with x.y.z; add commit hash to archive/x.y.z.md
 - [ ] Ensure Read the Docs renders correctly for `stable` (triggered after new tag is pushed)
 - [ ] Run through a Release on the GitHub site
 - [ ] Place a release notice on the MOM6 forum

<!-- Delete sections with no content -->
# General Release Notes

# Bug Fixes

# API Changes

# Contributors
