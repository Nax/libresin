#!/usr/bin/env python

import os

version = None
with open('VERSION', 'r') as f:
  version = f.read().strip()

tag = "v%s" % version

print("Creating tag %s..." % tag)
os.system("git tag -a %s -m '%s'" % (tag, tag))
print("Pushing tag %s..." % tag)
os.system("git push origin %s" % tag)
print("Version %s released" % tag)
