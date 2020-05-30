#!/usr/bin/env python

import os
import gzip

from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES

class Annotations:

    SUFFIX = ".annot.gz"

    @staticmethod
    def readSNPs(f):
        with (gzip.open if f.endswith(".gz") else open)(f, 'rt') as ff:
            ff.readline()
            return [ '\t'.join(line.strip().split('\t')[:5]) for line in ff ]

    @staticmethod
    def validateDirectory(directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "annotations"):
        for chromosome in chromosomes:
            path = os.path.join(directory, "%s.%s%s" % (prefix, chromosome, Annotations.SUFFIX))
            if not os.path.exists(path):
                raise FileNotFoundError("incomplete annotations: missing %s" % path) 

    def __init__(self, directory, prefix = "annotations", chromosomes = HUMAN_SOMATIC_CHROMOSOMES):
        Annotations.validateDirectory(directory, chromosomes, prefix)
        self.directory = directory
        self.prefix = prefix
        self.chromosomes = set(chromosomes)

    def __getitem__(self, k):
        if k not in self.chromosomes:
            raise KeyError("requested invalid chromosome %s from Annotations object" % k)
        return os.path.join(self.directory, "%s.%s%s" % (self.prefix, k, Annotations.SUFFIX))
