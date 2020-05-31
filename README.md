# ldr: Dockerized LD regression

This repository provides a Dockerized version of `ldsc`, a tool for performing LD Score regression. It is intended to facilitate the production of custom binary annotations for SNPs and computing partitioned heritability as described in [Finucane, HK, et al. Partitioning heritability by functional annotation using genome-wide association summary statistics. Nature Genetics, 2015](https://www.nature.com/articles/ng.3404). The core functionality of the tool was implemented by Bulik-Sullivan et. al. and is available at [https://github.com/bulik/ldsc](https://github.com/bulik/ldsc).

## Running

We encourage running this software as a Docker image, which is publicly available through GitHub packages. To pull the image, first [install Docker](https://docs.docker.com/engine/install/), then login to GitHub packages:
```
cat github.token.txt | docker login docker.pkg.github.com -u your-github-username --password-stdin
```
where `github.token.txt` contains an access token with access to GitHub packages generated [here](https://github.com/settings/tokens). Once you have logged in, run:
```
docker pull docker.pkg.github.com/weng-lab/ldr/ldr:latest
```
### Annotating SNPs
To perform custom partitioned heritability analysis, SNPs must first be annotated according to their intersection with custom sets of annotations. This package will generate custom binary annotations in the approriate format. Run
```
docker run \
    --volume /path/to/inputs:/input \
    --volume /path/to/annotations:/output \
    docker.pkg.github.com/weng-lab/ldr/ldr:latest \
    python3 -m ldr.annotations \
        --files /input/annotations1.bed /input/annotations2.bed ... \
        --file-output-prefix annotations \
        --output-directory /output
```

By default, this will use the HapMap3 SNPs provided in the baseline model described in the [LDSC wiki](https://github.com/bulik/ldsc/wiki), and it will estimate LD scores for the annotations as described in the final section of this tutorial [https://github.com/bulik/ldsc/wiki/LD-Score-Estimation-Tutorial](https://github.com/bulik/ldsc/wiki/LD-Score-Estimation-Tutorial). The output directory produced by this script may be used directly as input to partitioned heritability calculations:
```
docker run \
    --volume /path/to/annotations:/input \
    --volume /path/to/output:/output \
    docker.pkg.github.com/weng-lab/ldr/ldr:latest \
    python3 -m ldr.h2 \
        --ld-scores /input \
        --ld-prefix annotations \
        --summary-statistics summary-stats.txt > /output/partitioned-heritability.txt
```

This will perform partitioned heritability computations on the summary statistics in `summary-stats.txt` given the annotations computed above, and will write results to `/path/to/output/partitioned-heritability.txt` outside the Docker image. The summary statistics must be in the format described in the [partitioned heritability tutorial](https://github.com/bulik/ldsc/wiki/Partitioned-Heritability).
## For developers
Contributions to the code are welcome via pull request. First clone this repo:
```
git clone git@github.com:/weng-lab/ldr
```
After making changes, run unit tests with
```
scripts/test.sh
```
