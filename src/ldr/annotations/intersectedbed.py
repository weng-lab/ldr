#!/usr/bin/env python

import os
import tempfile

class IntersectedBED:

    @staticmethod
    def intersectRegions(snps, regions, bed):
        if os.system("bedtools intersect -a \"{snps}\" -b \"{regions}\" -wa | sort | uniq > {bed}".format(
            snps = snps, regions = regions, bed = bed
        )) != 0:
            raise ChildProcessError("failed to intersect {snps} with {regions}; check that they are valid BED files".format(
                snps = snps, regions = regions
            ))

    def __init__(self, snps, regions):
        self.snps = snps
        self.regions = regions

    def __enter__(self):
        self.tempfile = tempfile.NamedTemporaryFile('rt')
        IntersectedBED.intersectRegions(self.snps, self.regions, self.tempfile.name)
        return self.tempfile
    
    def __exit__(self, *args):
        self.tempfile.close()
