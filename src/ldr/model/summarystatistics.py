#!/usr/bin/env python

import os
import tempfile
import requests
import bz2

class FormattedSummaryStatistics:

    @staticmethod
    def formatSummaryStatistics(raw, snps, prefix):
        command = "munge_sumstats.py --sumstats {raw} --merge-alleles {snps} --out {out} --a1-inc".format(
            snps = snps, raw = raw, out = prefix
        )
        if os.system(command) != 0:
            raise ChildProcessError("failed to format summary statistics with command %s" % command)

    def __init__(self, raw, snps, skip = False):
        self.raw = raw
        self.snps = snps
        self.skip = skip
    
    def __enter__(self):
        self.tempfile = tempfile.NamedTemporaryFile(suffix = ".sumstats.gz")
        if not self.skip:
            FormattedSummaryStatistics.formatSummaryStatistics(self.raw, self.snps, self.tempfile.name[:-12])
        else:
            os.system("cp %s %s" % (self.raw, self.tempfile.name))
        return self.tempfile.name
    
    def __exit__(self, *args):
        self.tempfile.close()
