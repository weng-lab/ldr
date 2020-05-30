#!/usr/bin/env python

import os
import tempfile

from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES, BASELINE_WEIGHTS_URL
from ..utilities.utilities import untar

class Weights:

    SUFFIX = ".l2.ldscore.gz"

    @staticmethod
    def validateDirectory(directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "weights.hm3_noMHC"):
        for chromosome in chromosomes:
            path = os.path.join(directory, "%s.%s%s" % (prefix, chromosome, Weights.SUFFIX))
            if not os.path.exists(path):
                raise FileNotFoundError("incomplete weights: missing %s" % path)            
    
    @classmethod
    def fromTar(cls, path, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, tarPrefix = '.', prefix = "weights.hm3_noMHC"):
        if untar(path, directory) != 0:
            raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % path)
        return cls(os.path.join(directory, prefix), chromosomes, prefix)
    
    @classmethod
    def fromBaselineWeights(cls, directory):
        try:
            cls.validateDirectory(os.path.join(directory, "1000G_Phase3_weights_hm3_no_MHC"), prefix = "weights.hm3_noMHC")
        except FileNotFoundError:
            with tempfile.NamedTemporaryFile(suffix = ".tar.gz") as tar:
                if os.system("wget {url} -O {tar}".format(url = BASELINE_WEIGHTS_URL, tar = tar.name)) != 0:
                    raise ChildProcessError("failed to save %s to %s; check your network connetion and try again" % (BASELINE_WEIGHTS_URL, tar))
                if untar(tar.name, directory) != 0:
                    raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % tar.name)
        return cls(os.path.join(directory, "1000G_Phase3_weights_hm3_no_MHC"))

    def __init__(self, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "weights.hm3_noMHC"):
        Weights.validateDirectory(directory, prefix = prefix)
        self.directory = directory
        self.chromosomes = chromosomes
        self.prefix = prefix

    def fileNamePrefix(self):
        return os.path.join(self.directory, self.prefix + '.')
