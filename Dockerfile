FROM ubuntu:20.04

COPY src/ldr /ldr/

RUN apt-get update && apt-get install -y python3 python3-pip git curl python3-dev build-essential wget bedtools && \
    git clone https://github.com/weng-lab/ldsc.git && cd ldsc && \
    grep -v pd.set.option..precision ldsc.py > t && mv t ldsc.py && chmod +x ldsc.py && \
    pip3 install scipy pandas numpy bitarray requests joblib && \
    apt-get remove -y git curl python3-dev build-essential python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /ldsc/ldsc.py /bin/ldsc.py && \
    ln -s /ldsc/munge_sumstats.py /bin/munge_sumstats.py && \
    ln -s /bin/python3 /bin/python
