# Big Mem `x86_64`

This is a large memory node running Ubuntu 20.04.2 LTS.

## FRE-NCtools

```
$ git clone
$ cd FRE-NCtools
$ autoreconf -i
```

### tests

Test13 contains the basics we need to create a simple regional
model.  It looks like we need to create a vertical grid as
well as a horzontal grid so `make_topog` will succeed.
