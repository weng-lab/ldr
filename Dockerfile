FROM ubuntu:20.04

COPY src/ldr /ldr/

RUN apt-get update && apt-get install -y python3 python3-pip git curl python3-dev build-essential && \
    git clone https://github.com/weng-lab/ldsc.git && cd ldsc && \
    pip3 install scipy pandas numpy bitarray requests && \
    apt-get remove -y git curl python3-dev build-essential python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /ldsc/ldsc.py /bin/ldsc.py && \
    ln -s /ldsc/munge_sumstats.py /bin/munge_sumstats.py
