#!/usr/bin/env python

import tempfile
import sys
import argparse
import os

from .partitionedheritability import PartitionedHeritability
from ..model.ld import LDScores
from ..model.weights import Weights
from ..model.frequencies import Frequencies
from ..model.summarystatistics import FormattedSummaryStatistics
from ..model.hapmap3 import HapMap3SNPs
from ..utilities.utilities import readSNPList
from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES

def parseArgs():
    parser = argparse.ArgumentParser("perform partitioned heritability analysis")
    parser.add_argument("--chromosomes", type = str, help = "comma-separated list of chromosomes; defaults to human somatic", default = None)
    parser.add_argument("--ld-scores", type = str, help = "path to LD scores and annotations, either directory or TAR; defaults to Broad baseline model", default = None)
    parser.add_argument("--ld-prefix", type = str, help = "LD score file name prefix; defaults to baseline", default = "baseline")
    parser.add_argument("--ld-tar-prefix", type = str, help = "LD TAR root directory; defaults to .", default = ".")
    parser.add_argument("--weights", type = str, help = "path to regression weights, either directory or TAR; defaults to 1000 Genomes", default = None)
    parser.add_argument("--weights-prefix", type = str, help = "regression weight file name prefix; defaults to 1000G prefix", default = "weights")
    parser.add_argument("--weights-tar-prefix", type = str, help = "regression weight TAR root directory; defaults to .", default = ".")
    parser.add_argument("--frequencies", type = str, help = "path to allele frequencies, either directory or TAR; defaults to 1000 Genomes", default = None)
    parser.add_argument("--frequencies-prefix", type = str, help = "allele frequencies file name prefix; defaults to 1000G prefix", default = "1000G_Phase3_frq")
    parser.add_argument("--frequencies-tar-prefix", type = str, help = "allele frequencies TAR root directory; defaults to .", default = ".")
    parser.add_argument("--summary-statistics", type = str, help = "path to summary statistics", required = True)
    parser.add_argument("--snp-list", type = str, help = "path to list of SNPs to use in formatting summary statistics; defaults to HapMap3", default = None)
    parser.add_argument("--print-coefficients", action = "store_true", help = "when categories are overlapping, print coefficients as well as heritabilities", default = False)
    parser.add_argument("--skip-munge", action = "store_true", help = "specifies that summary statistics are already in a valid format for input to LDSC", default = False)
    return parser.parse_args()

def main():

    args = parseArgs()
    temporaryDirectories = {
        "ld": None if args.ld_scores is not None else tempfile.TemporaryDirectory(),
        "weights": None if args.weights is not None else tempfile.TemporaryDirectory(),
        "frequencies": None if args.frequencies is not None else tempfile.TemporaryDirectory()
    }
    chromosomes = args.chromosomes.split(',') if args.chromosomes is not None else HUMAN_SOMATIC_CHROMOSOMES
    snps = None if args.snp_list is None else readSNPList(args.snp_list)

    ld = LDScores.fromBaselineModel(temporaryDirectories["ld"].name) if args.ld_scores is None else (
        LDScores.fromTar(
            args.ld_scores, temporaryDirectories["ld"].name, chromosomes, args.ld_tar_prefix, args.ld_prefix
        ) if not os.path.isdir(args.ld_scores) else LDScores(args.ld_scores, chromosomes, args.ld_prefix)
    )

    weights = Weights.fromBaselineWeights(temporaryDirectories["weights"].name) if args.weights is None else (
        Weights.fromTar(
            args.weights, temporaryDirectories["weights"].name, chromosomes, args.weights_tar_prefix, args.weights_prefix
        ) if not os.path.isdir(args.weights) else Weights(args.weights, chromosomes, args.weights_prefix)
    )

    frequencies = Frequencies.fromBaselineFrequencies(temporaryDirectories["frequencies"].name) if args.frequencies is None else (
        Frequencies.fromTar(
            args.frequencies, temporaryDirectories["frequencies"].name, chromosomes, args.frequencies_tar_prefix, args.frequencies_prefix
        ) if not os.path.isdir(args.frequencies) else Frequencies(args.frequencies, chromosomes, args.frequencies_prefix)
    )

    with (HapMap3SNPs.fromBroad() if snps is None else HapMap3SNPs(snps)) as snplist:
        with FormattedSummaryStatistics(args.summary_statistics, snplist, args.skip_munge) as f:
            with PartitionedHeritability(f, ld, weights, frequencies, print_coefficients = args.print_coefficients) as p:
                print(p.read())

    for _, v in temporaryDirectories.items():
        if v is not None: v.cleanup()

    return 0

if __name__ == "__main__":
    sys.exit(main())
