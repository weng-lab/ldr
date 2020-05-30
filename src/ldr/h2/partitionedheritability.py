#!/usr/bin/env python

import os
import tempfile

from ..model.summarystatistics import FormattedSummaryStatistics
from ..model.ld import LDScores
from ..model.frequencies import Frequencies
from ..model.weights import Weights

class PartitionedHeritability:

    @staticmethod
    def partitionHeritability(summaryStatistics, ld, weights, frequencies, output):
        command = """
            ldsc.py \
                --h2 {summaryStatistics} \
                --ref-ld-chr {ld} \
                --w-ld-chr {weights} \
                --frqfile-chr {frequencies} \
                --overlap-annot \
                --out {output}
        """.format(
            summaryStatistics = summaryStatistics,
            ld = ld.fileNamePrefix(),
            weights = weights.fileNamePrefix(),
            frequencies = frequencies.fileNamePrefix(),
            output = output
        )
        if os.system(command) != 0:
            raise ChildProcessError("failed to perform heritability partitioning with command %s" % command)

    def __init__(self, summaryStatistics, ld, weights, frequencies, prefix = "h2"):
        self.summaryStatistics = summaryStatistics
        self.ld = ld
        self.weights = weights
        self.frequencies = frequencies
        self.prefix = prefix

    def __enter__(self):
        self.directory = tempfile.TemporaryDirectory()
        PartitionedHeritability.partitionHeritability(
            self.summaryStatistics, self.ld, self.weights, self.frequencies,
            os.path.join(self.directory.name, self.prefix)
        )
        self.file = open(os.path.join(self.directory.name, self.prefix + ".results"), 'rt')
        return self.file
    
    def __exit__(self, *args):
        self.directory.cleanup()
        self.file.close()
