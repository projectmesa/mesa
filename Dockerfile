FROM python:3.10-slim
LABEL maintainer="rht <rhtbot@protonmail.com>"

# To use this Dockerfile:
# 1. `docker build . -t mymesa_image`
# 2. `docker run --name mymesa_instance -p 8521:8521 -it mymesa_image`
# 3. In your browser, visit http://127.0.0.1:8521
#
# Currently, this Dockerfile defaults to running the Wolf-Sheep model, as an
# illustration. If you want to run a different example, simply change the
# MODEL_DIR variable below to point to another model, e.g.
# examples/sugarscape_cg or path to your custom model.
# You specify the MODEL_DIR (relative to this Git repo) by doing:
# `docker run --name mymesa_instance -p 8521:8521 -e MODEL_DIR=examples/sugarscape_cg -it mymesa_image`
# Note: the model directory MUST contain a run.py file.

ENV MODEL_DIR=examples/wolf_sheep

# Don't buffer output:
# https://docs.python.org/3.10/using/cmdline.html?highlight=pythonunbuffered#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mesa

COPY . /opt/mesa

EXPOSE 8521/tcp

# Important: we don't install python3-dev, python3-pip and so on because doing
# so will install Python 3.9 instead of the already available Python 3.10 from
# the base image.
# The following RUN command is still provided for context.
# RUN apt-get update && apt-get upgrade -y -o Dpkg::Options::="--force-confold" \
#    && apt-get install -y --no-install-recommends \
#    build-essential \
#    python3-dev \
#    python3-pip \
#    python3-setuptools \
#    python3-wheel \
#    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -e /opt/mesa

CMD ["sh", "-c", "cd $MODEL_DIR && python3 run.py"]
