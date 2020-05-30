#!/usr/bin/env python

import os
import tempfile
import unittest
import hashlib

from ldr.utilities.utilities import untar

class TestUntarOutput:

    def __init__(self, tar):
        self.tar = tar
    
    def __enter__(self):
        self.directory = tempfile.TemporaryDirectory()
        untar(self.tar, self.directory.name)
        return self.directory
    
    def __exit__(self, *args):
        self.directory.cleanup()

class TestUtilities(unittest.TestCase):

    def test_untar(self):
        with TestUntarOutput(os.path.join(os.path.dirname(__file__), "resources", "test.tar")) as tar:
            self.assertTrue(os.path.exists(os.path.join(tar.name, "test", "test")))
            with open(os.path.join(tar.name, "test", "test"), 'rt') as f:
                self.assertEqual(f.read(), "test\n")

    def test_untar_gzipped(self):
        with TestUntarOutput(os.path.join(os.path.dirname(__file__), "resources", "test.tar.gz")) as tar:
            self.assertTrue(os.path.exists(os.path.join(tar.name, "test", "test")))
            with open(os.path.join(tar.name, "test", "test"), 'rt') as f:
                self.assertEqual(f.read(), "test\n")
