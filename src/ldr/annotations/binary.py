#!/usr/bin/env python

import os
import gzip

from .annotations import Annotations
from .annotationsbed import AnnotationsBed
from .intersectedbed import IntersectedBED
from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES

class BinaryAnnotations(Annotations):

    @staticmethod
    def annotationVector(snpbed, regions):
        snps = [ line.strip().split()[3] for line in snpbed ]
        with IntersectedBED(snpbed.name, regions) as f:
            intersected = { line.strip().split()[3] for line in f }
        snpbed.seek(0)
        return [ 1 if x in intersected else 0 for x in snps ]

    @classmethod
    def fromTemplate(cls, template, directory, *files, prefix = "annotations", chromosomes = HUMAN_SOMATIC_CHROMOSOMES):
        if type(template) is not Annotations:
            raise ValueError("BinaryAnnotations template must be of type Annotations; got %s" % type(template))
        for chromosome in chromosomes:
            snps = Annotations.readSNPs(template[chromosome])
            with AnnotationsBed(template[chromosome]) as wbed:
                with open(wbed.name, 'rt') as bed:
                    annotationMatrix = [ BinaryAnnotations.annotationVector(bed, x) for x in files ]
            with gzip.open(os.path.join(directory, "%s.%s%s" % (prefix, chromosome, Annotations.SUFFIX)), 'wt') as o:
                o.write("CHR\tBP\tSNP\tCM\tbase\t" + '\t'.join(files) + '\n' + '\n'.join([
                    snps[i] + '\t' + '\t'.join([ str(annotationMatrix[j][i]) for j in range(len(files)) ])
                    for i, x in enumerate(annotationMatrix[0])
                ]) + '\n')
        return cls(directory, prefix, chromosomes)

    def __init__(self, directory, prefix = "annotations", chromosomes = HUMAN_SOMATIC_CHROMOSOMES):
        Annotations.__init__(self, directory, prefix, chromosomes)
