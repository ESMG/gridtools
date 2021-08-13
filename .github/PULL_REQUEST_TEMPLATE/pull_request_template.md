<details>
  <summary><i>submission notes</i></summary>

```
**Important:** Please sanitize/remove any confidential info like
usernames, passwords, org names, product names/ids, access tokens,
client ids/secrets, or anything else you don't wish to share.

You may also delete this submission notes header if you'd like.
Thank you for contributing!
```
</details>

### Problem

What Bug or Missing Feature does this PR address? (A short summary
is preferred over links)

### Solution

How does this PR address the problem stated above? (Describing the
solutions implemented in code will facilitate a smooth discussion,
review and testing of this PR)

### Test/Example

Supply a test or example that would help with
replicating the bug or demonstration of the new
feature.

### Code

```python
#!/bin/env python3
# conda: gridTools

import sys, os, logging
import cartopy
from gridtools.gridutils import GridUtils

# Initialize a grid object
grd = GridUtils()
grd.printMsg("At this point, we have initialized a GridUtils() object.")
grd.printMsg("")
```

### Diagnostics

If you are able to create a grid, perform an `ncdump -h` of
the saved grid file.  Copy and paste the contents of the
"global attributes:" here.  This gives the developers a
quick look at the version of gridtools, commit and software
versions of python packages.

```text
From ncdump -h:

//global attributes
	:code_version =
	:software_version =
```

### References

Links to the (Community MOM6 Forum)[https://bb.cgd.ucar.edu/cesm/forums/mom6.148/],
Docs, Other Issues, etc..

---

### Completeness

User tasks:
- [ ] Pull request should target the **dev** branch, see [CONTRIBUTING](CONTRIBUTING.md)
- [ ] Problem and/or Solution clearly stated
- [ ] Referred to example or provided example to replicate the bug or feature

Developer tasks (after PR submission):
- [ ] Review
- [ ] Diagnose/Assign; add to [TODO](docs/development/TODO.md) and/or provision to a milestone
- [ ] Add documentation and/or tests
- [ ] Add to [CHANGELOG](docs/development/CHANGELOG.md)
- [ ] Follow [DEPLOY](docs/development/DEPLOY.md) template
