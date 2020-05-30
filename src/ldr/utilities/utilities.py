#!/usr/bin/env python

import os

def untar(path, directory):
    return os.system("tar -C {directory} -{z}xf {path}".format(
        z = 'z' if path.endswith(".gz") else "",
        directory = directory, path = path
    ))

def readSNPList(f):
    with open(f, 'r') as ff:
        return ff.read()
