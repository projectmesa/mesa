FROM phusion/baseimage:0.11
# developer Dockerfile for mesa development, installs from local git checkout
LABEL maintainer="Allen Lee <allen.lee@asu.edu>"

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /opt/mesa

COPY . /opt/mesa

RUN apt-get update && apt-get upgrade -y -o Dpkg::Options::="--force-confold" \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -e /opt/mesa
