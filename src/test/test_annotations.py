#!/usr/bin/env python

import gzip
import os
import unittest
import hashlib
import tempfile

from ldr.annotations.annotationsbed import AnnotationsBed
from ldr.annotations.annotations import Annotations
from ldr.annotations.intersectedbed import IntersectedBED
from ldr.annotations.binary import BinaryAnnotations

class TestUtilities(unittest.TestCase):

    def test_annotations_bed(self):
        with AnnotationsBed(os.path.join(os.path.dirname(__file__), "resources", "ld", "baseline.1.annot.gz")) as bed:
            with open(bed.name, 'rt') as f:
                self.assertEqual(hashlib.md5(f.read().encode("utf-8")).hexdigest(), "8d37f1807f90b3e24a06b88d80c3bbc8")

    def test_intersected_bed(self):
        with IntersectedBED(
            os.path.join(os.path.dirname(__file__), "resources", "test.bed"),
            os.path.join(os.path.dirname(__file__), "resources", "test2.bed")
        ) as ibed:
            self.assertEqual(hashlib.md5(ibed.read().encode("utf-8")).hexdigest(), "7966fb45b8949b6c2915c1f6c94578be")

    def test_binary_annotations(self):
        with tempfile.TemporaryDirectory() as d:
            BinaryAnnotations.fromTemplate(
                Annotations(os.path.join(os.path.dirname(__file__), "resources", "ld"), "baseline", [ "1", "19" ]),
                d, os.path.join(os.path.dirname(__file__), "resources", "test2.bed"),
                chromosomes = [ "1", "19" ], prefix = "annotations",
            )
            self.assertTrue(os.path.exists(os.path.join(d, "annotations.1.annot.gz")))
            os.system("cp %s %s" % (os.path.join(d, "annotations.19.annot.gz"), "/test"))
            with gzip.open(os.path.join(d, "annotations.1.annot.gz"), 'rt') as f:
                f.readline()
                self.assertEqual(hashlib.md5(
                    f.read().replace("\t%s" % os.path.join(d, "annotations.1.annot.gz"), "").encode("utf-8")
                ).hexdigest(), "334cf2014c299b7a246d29209c1b05b4"
            )
            self.assertTrue(os.path.exists(os.path.join(d, "annotations.19.annot.gz")))
            with gzip.open(os.path.join(d, "annotations.19.annot.gz"), 'rt') as f:
                f.readline()
                self.assertEqual(hashlib.md5(
                    f.read().replace("\t%s" % os.path.join(d, "annotations.19.annot.gz"), "").encode("utf-8")
                ).hexdigest(), "c944e7ab5966c5f2667fb0c880ac4849"
            )
