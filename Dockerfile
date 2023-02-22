FROM python:3.12-bookworm

RUN apt-get update && \
    apt-get install -y \
        gdal-bin \
        parallel \
        postgresql-client \
        python3-virtualenv

WORKDIR /opt/imposm
RUN wget https://github.com/omniscale/imposm3/releases/download/v0.11.1/imposm-0.11.1-linux-x86-64.tar.gz && \
    tar -xvzf imposm-0.11.1-linux-x86-64.tar.gz && \
    ln -s /opt/imposm/imposm-0.11.1-linux-x86-64/imposm /usr/bin/imposm

WORKDIR /opt/bano

ADD requirements.txt .
RUN pip install -r requirements.txt
