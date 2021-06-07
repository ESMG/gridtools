# Releases

This document the steps needed for a complete release.

# Checklist

 - [ ] Ensure `binder/environment.yml` is in sync with `conda/gridTools_export-linux-64.yml`
 - [ ] Ensure dev passes continuous integration tests with submitted PR
 - [ ] Ensure release/version is properly updated in `gridtools/__init__.py`
 - [ ] Commit with "Release x.y.z"
 - [ ] Add and commit a tag with x.y.z
 - [ ] Run through a Release on the github site
