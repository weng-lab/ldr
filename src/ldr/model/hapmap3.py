#!/usr/bin/env python

import os
import tempfile
import requests
import bz2

from ..constants.constants import HAPMAP3_SNPS_URL

class HapMap3SNPs:

    @classmethod
    def fromBroad(cls, withoutHeader = False):
        return cls(bz2.decompress(requests.get(HAPMAP3_SNPS_URL).content).decode(), withoutHeader = withoutHeader)

    def __init__(self, data, withoutHeader = False):
        self.data = data
        self.withoutHeader = withoutHeader
    
    def __enter__(self):
        self.tempfile = tempfile.NamedTemporaryFile('w')
        self.tempfile.write(
            self.data if not self.withoutHeader else os.linesep.join([
                x.strip().split()[0] for x in self.data.split('\n')[1:]
                if len(x.strip().split()) > 0
            ]) + os.linesep
        )
        self.tempfile.flush()
        return self.tempfile.name
    
    def __exit__(self, *args):
        self.tempfile.close()
