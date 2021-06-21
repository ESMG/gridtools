# Releases

This document the steps needed for a complete release.  Copy to
release folder as X.Y.Z.md and fill out.

# Checklist

 - [ ] Verify operation of example notebooks
 - [ ] Verify operation of example scripts
 - [ ] Resync environments
   - [ ] Resync gridTools_export-linux-64.yml without pip modules
   - [ ] Add minimal pip modules to requirements.txt
   - [ ] Ensure `binder/environment.yml` is in sync
         with `conda/gridTools_export-linux-64.yml`
 - [ ] Ensure release/version is properly updated in `gridtools/__init__.py`
 - [ ] Modify any test CI Github Actions
 - [ ] Update any tests performed by pytest
 - [ ] Update TODOs.md
 - [ ] Ensure dev passes continuous integration tests with submitted PR
 - [ ] Commit with "Release x.y.z"
   - [ ] Reverify mybinder.org operation
   - [ ] Ensure CI/Actions continue to pass
   - [ ] Ensure ReadtheDocs renders correctly
   - [ ] Ensure MDs on github renders correctly
 - [ ] Add and commit a tag with x.y.z
 - [ ] Run through a Release on the github site

# General Release Notes
