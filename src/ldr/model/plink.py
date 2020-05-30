#!/usr/bin/env python

import os
import tempfile

from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES, PLINK_1000G_URL
from ..utilities.utilities import untar

class Plink:

    SUFFIXES = [ ".fam", ".bim", ".bed" ]

    @staticmethod
    def validateDirectory(directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "1000G.EUR.QC"):
        for chromosome in chromosomes:
            for suffix in Plink.SUFFIXES:
                path = os.path.join(directory, "%s.%s%s" % (prefix, chromosome, suffix))
                if not os.path.exists(path):
                    raise FileNotFoundError("incomplete PLINK directory: missing %s" % path)            
    
    @classmethod
    def fromTar(cls, path, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, tarPrefix = '.', prefix = "1000G.EUR.QC"):
        if untar(path, directory) != 0:
            raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % path)
        return cls(os.path.join(directory, tarPrefix), chromosomes, prefix)

    @classmethod
    def fromBaselineModel(cls, directory):
        try:
            cls.validateDirectory(os.path.join(directory, "1000G_EUR_Phase3_plink"), prefix = "1000G.EUR.QC")
        except FileNotFoundError:
            with tempfile.NamedTemporaryFile(suffix = ".tar.gz") as tar:
                if os.system("wget {url} -O {tar}".format(url = PLINK_1000G_URL, tar = tar.name)) != 0:
                    raise ChildProcessError("failed to save %s to %s; check your network connetion and try again" % (PLINK_1000G_URL, tar))
                if untar(tar.name, directory) != 0:
                    raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % tar.name)
        return cls(os.path.join(directory, "1000G_EUR_Phase3_plink"))

    def __init__(self, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "1000G.EUR.QC"):
        Plink.validateDirectory(directory, chromosomes, prefix)
        self.directory = directory
        self.chromosomes = chromosomes
        self.prefix = prefix

    def fileNamePrefix(self, chromosome):
        if chromosome not in self.chromosomes:
            raise ValueError("PLINK directory does not contain files for chromosome %s" % chromosome)
        return os.path.join(self.directory, self.prefix + ".%s" % chromosome)
