#!/usr/bin/env python

import os
import sys
import gzip

from datetime import datetime
from joblib import Parallel, delayed

from .annotations import Annotations
from .annotationsbed import AnnotationsBed
from .intersectedbed import IntersectedBED
from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES

def annotationVector(snpbedp, regions):
    with open(snpbedp, 'rt') as snpbed:
        snps = [ line.strip().split()[3] for line in snpbed ]
        with IntersectedBED(snpbedp, regions) as f:
            intersected = { line.strip().split()[3] for line in f }
        return [ 1 if x in intersected else 0 for x in snps ]

class BinaryAnnotations(Annotations):

    @classmethod
    def fromTemplate(cls, template, directory, *files, prefix = "annotations", chromosomes = HUMAN_SOMATIC_CHROMOSOMES, j = 1, extend = False):
        if type(template) is not Annotations:
            raise ValueError("BinaryAnnotations template must be of type Annotations; got %s" % type(template))
        for chromosome in chromosomes:
            print('[' + str(datetime.now()) + "] generating annotations for chromosome %s" % chromosome, file = sys.stderr)
            snps = Annotations.readSNPs(template[chromosome])
            with AnnotationsBed(template[chromosome]) as wbed:
                annotationMatrix = Parallel(n_jobs = j)(delayed(annotationVector)(wbed.name, x) for x in files)
            with gzip.open(os.path.join(directory, "%s.%s%s" % (prefix, chromosome, Annotations.SUFFIX)), 'wt') as o:
                if not extend:
                    o.write("CHR\tBP\tSNP\tCM\tbase\t" + '\t'.join([ x.replace(' ', '_') for x in files ]) + '\n' + '\n'.join([
                        snps[i] + '\t' + '\t'.join([ str(annotationMatrix[j][i]) for j in range(len(files)) ])
                        for i, x in enumerate(annotationMatrix[0])
                    ]) + '\n')
                else:
                    snpmap = { x: i for i, x in enumerate(snps) }
                    with (gzip.open if template[chromosome].endswith(".gz") else open)(template[chromosome], 'rt') as f:
                        o.write(f.readline().strip() + '\t'.join([ x.replace(' ', '_') for x in files ]) + '\n')
                        for line in f:
                            i = snpmap['\t'.join(line.strip().split('\t')[:5])]
                            o.write(line.strip() + '\t'.join([ str(annotationMatrix[j][i]) for j in range(len(files)) ]) + '\n')
        return cls(directory, prefix, chromosomes)

    def __init__(self, directory, prefix = "annotations", chromosomes = HUMAN_SOMATIC_CHROMOSOMES):
        Annotations.__init__(self, directory, prefix, chromosomes)
