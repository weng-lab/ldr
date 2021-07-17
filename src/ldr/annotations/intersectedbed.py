#!/usr/bin/env python

import os
import tempfile

class IntersectedBED:

    @staticmethod
    def intersectRegions(snps, regions, bed, wb = False):
        if os.system("bedtools intersect -a \"{snps}\" -b \"{regions}\" -wa {wb} | sort | uniq > {bed}".format(
            snps = snps, regions = regions, bed = bed, wb = "-wb" if wb else ""
        )) != 0:
            raise ChildProcessError("failed to intersect {snps} with {regions}; check that they are valid BED files".format(
                snps = snps, regions = regions
            ))

    def __init__(self, snps, regions, wb = False):
        self.snps = snps
        self.regions = regions
        self.wb = wb

    def __enter__(self):
        self.tempfile = tempfile.NamedTemporaryFile('rt')
        IntersectedBED.intersectRegions(self.snps, self.regions, self.tempfile.name, wb = self.wb)
        return self.tempfile
    
    def __exit__(self, *args):
        self.tempfile.close()
