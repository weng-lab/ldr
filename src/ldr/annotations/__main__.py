#!/usr/bin/env python

import sys
import os
import argparse
import tempfile

from .binary import BinaryAnnotations
from .annotations import Annotations
from ..constants.constants import HUMAN_SOMATIC_CHROMOSOMES
from ..model.ld import LDScores
from ..model.plink import Plink
from ..utilities.utilities import readSNPList
from ..model.hapmap3 import HapMap3SNPs

def parseArgs():
    parser = argparse.ArgumentParser("generate custom annotations for partitioned heritability calculations")
    parser.add_argument("--template", type = str, help = "path to template annotations; defaults to Broad baseline model", default = None)
    parser.add_argument("--template-prefix", type = str, help = "prefix of template annotation files; defaults to 'baseline'", default = "baseline")
    parser.add_argument("--output-directory", type = str, help = "path to directory in which to write output", required = True)
    parser.add_argument("--chromosomes", type = str, help = "comma-separated list of chromosomes; defaults to human somatic", default = None)
    parser.add_argument("--file-output-prefix", type = str, help = "prefix to use when writing output; default is 'annotations'", default = "annotations")
    parser.add_argument("--files", type = str, nargs = '+', help = "paths to BED files to intersect to generate annotations")
    parser.add_argument("--plink", type = str, help = "path to PLINK, either TAR or directory; defaults to 1000 genomes", default = None)
    parser.add_argument("--plink-prefix", type = str, help = "PLINK file name prefix; defaults to 1000 genomes", default = "1000G.EUR.QC")
    parser.add_argument("--plink-tar-prefix", type = str, help = "PLINK TAR root directory; defaults to none", default = ".")
    parser.add_argument("--snp-list", type = str, help = "path to list of SNPs to use in formatting summary statistics; defaults to HapMap3", default = None)
    parser.add_argument("--extend-annotations", action = "store_true", default = False, help = "if set, extends the given existing set of annotations")
    parser.add_argument("--j", type = int, help = "number of cores", default = 1)
    return parser.parse_args()

def main():
    
    args = parseArgs()
    if not os.path.exists(args.output_directory): os.system("mkdir -p %s" % args.output_directory)

    chromosomes = args.chromosomes.split(',') if args.chromosomes is not None else HUMAN_SOMATIC_CHROMOSOMES
    snps = None if args.snp_list is None else readSNPList(args.snp_list)
    temporaryDirectories = {
        "plink": None if args.plink is not None else tempfile.TemporaryDirectory(),
        "ld": None if args.template is not None else tempfile.TemporaryDirectory()
    }

    template = args.template
    if template is None:
        ld = LDScores.fromBaselineModel(temporaryDirectories["ld"].name)
        template = os.path.dirname(ld.fileNamePrefix())
    
    plink = Plink.fromTar(
        args.plink, temporaryDirectories["plink"].name, args.chromosomes, args.plink_tar_prefix, args.plink_prefix
    ) if args.plink is not None and not os.path.isdir(args.plink) else (
        Plink(args.plink, args.chromosomes, args.plink_prefix) if args.plink is not None else Plink.fromBaselineModel(temporaryDirectories["plink"].name)
    )

    try:
        annotations = BinaryAnnotations.fromTemplate(
            Annotations(template, args.template_prefix, chromosomes),
            args.output_directory, *args.files, prefix = args.file_output_prefix, chromosomes = chromosomes, j = args.j,
            extend = args.extend_annotations
        )
        with (HapMap3SNPs.fromBroad(withoutHeader = True) if snps is None else HapMap3SNPs(snps, withoutHeader = True)) as snplist:
            LDScores.fromExistingAnnotations(
                annotations.directory, args.file_output_prefix, plink, snplist, chromosomes, args.j
            )
    except:
        for _, v in temporaryDirectories.items():
            if v is not None: v.cleanup()
        raise

    print("wrote annotations to %s" % args.output_directory, file = sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
