#!/usr/bin/env python

import os
import tempfile
import subprocess
from joblib import Parallel, delayed

from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES, BASELINE_LD_URL
from ..utilities.utilities import untar

class LDScores:

    SUFFIXES = [ ".l2.M", ".l2.M_5_50", ".l2.ldscore.gz", ".annot.gz" ]

    @staticmethod
    def computeLD(annotations, plink, snplist, chromosome):
        print(chromosome, annotations, plink, snplist)
        if not annotations.endswith(".annot.gz"):
            raise ValueError("annotations file must end with .annot.gz; got %s" % annotations)
        command = [
            "ldsc.py", "--l2", "--ld-wind-cm", "1", "--bfile", plink.fileNamePrefix(chromosome),
            "--print-snps", snplist, "--annot", annotations, "--out", annotations[:-9]
        ]
        if subprocess.call(command) != 0:
            raise ChildProcessError("unable to generate LD scores using command %s" % ' '.join(command))

    @staticmethod
    def validateDirectory(directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "baseline"):
        for chromosome in chromosomes:
            for suffix in LDScores.SUFFIXES:
                path = os.path.join(directory, "%s.%s%s" % (prefix, chromosome, suffix))
                if not os.path.exists(path):
                    raise FileNotFoundError("incomplete LD scores: missing %s" % path)            

    @classmethod
    def fromExistingAnnotations(cls, directory, prefix, plink, snplist, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, j = 1):
        Parallel(n_jobs = j)(delayed(LDScores.computeLD)(
            os.path.join(directory, prefix + ".%s.annot.gz" % chromosome),
            plink, snplist, chromosome
        ) for chromosome in chromosomes)
        return cls(directory, chromosomes, prefix)

    @classmethod
    def fromTar(cls, path, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, tarPrefix = '.', prefix = "baseline"):
        if path.startswith("http://") or path.startswith("https://"):
            with tempfile.NamedTemporaryFile() as f:
                if os.system("wget {url} -O {tar}".format(url = path, tar = f.name)) != 0:
                    raise ChildProcessError("failed to save %s to %s; check your network connetion and try again" % (BASELINE_LD_URL, tar))
                if untar(f.name, directory) != 0:
                    raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % path)
        elif untar(path, directory) != 0:
            raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % path)
        return cls(os.path.join(directory, prefix), chromosomes, prefix)
    
    @classmethod
    def fromBaselineModel(cls, directory, prefix = None):
        if prefix is None: prefix = "baselineLD"
        try:
            cls.validateDirectory(os.path.join(directory, "baseline_v2.2"), prefix = prefix)
        except FileNotFoundError:
            with tempfile.NamedTemporaryFile(suffix = ".tar.gz") as tar:
                if os.system("wget {url} -O {tar}".format(url = BASELINE_LD_URL, tar = tar.name)) != 0:
                    raise ChildProcessError("failed to save %s to %s; check your network connetion and try again" % (BASELINE_LD_URL, tar))
                if untar(tar.name, directory) != 0:
                    raise ChildProcessError("failed to extract %s; check that it is an existing, valid TAR archive" % tar.name)
        return cls(os.path.join(directory, "baseline_v2.2"))

    def __init__(self, directory, chromosomes = HUMAN_SOMATIC_CHROMOSOMES, prefix = "baseline"):
        LDScores.validateDirectory(directory, chromosomes, prefix)
        self.directory = directory
        self.chromosomes = chromosomes
        self.prefix = prefix

    def fileNamePrefix(self):
        return os.path.join(self.directory, self.prefix + '.')
