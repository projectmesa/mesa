# The Mesa project publishes "official" code to:
# - Pip: https://pypi.org/project/Mesa
# - Docker Hub: Not yet!

# There is no official Mesa Docker image.  Use this example to build your own.

# You can build and run this Docker image with these commands:
# $ docker build . -t mymesa_image
# $ docker rm -f mymesa_instance
# $ docker run --name mymesa_instance -p 8521:8521/tcp -it mymesa_image 
# View at http://127.0.0.1:8521

# "bash" the instance like this:
# $ docker exec -it mymesa_instance /bin/bash 

# FOR SECURITY:
# - Don't use random Docker images, libraries, or napkins in the bin
# - Use official Docker images, or images packaged by the same people that made the library.
# - Otherwise, who knows what code is in that image?!

# This example Dockerfile packages the wolf_sheep example model.

# To use your own model, place your code in /opt/mesa/mymodel. 
# You have two options:

# OPTION A) COPY files into Docker image

# From your other codebase, do these steps:
# 1) Copy this Dockerfile into your model codebase
# 2) Replace `COPY examples/boid-flockers /opt/mesa/mymodel`
#       with `COPY [dir w/ your run.py] /opt/mesa/mymodel`
# 3) Follow steps to build and run above

# OPTION B) Mount a volume using docker-compose or kubernetes

# `docker-compose.yml` in this repo shows an example of this 
# models mounted in volumes must have their dependencies managed outside docker


# Example Dockerfile for wolf_sheep model
# Steps in this file are ordered least likly to change (top) to most likely to change (bottom)

# Use official python image from Docker team: https://hub.docker.com/_/python
FROM python:stretch

# Expose our port:
EXPOSE 8521/tcp

# Update OS
RUN apt-get update && apt-get upgrade -y 

# Don't buffer output: https://docs.python.org/3.7/using/cmdline.html?highlight=pythonunbuffered#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED=1 
# Cruft? Set locale to use UTF-8: http://www.iac.es/sieinvens/siepedia/pmwiki.php?n=Tutorials.LinuxLocale
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install pipenv
RUN pip install --upgrade pipenv

# As of now, we have:
# - debian stretch OS w/ updates
# - python3 from Docker team
# - pipenv from Pip
# - models can install mesa w/ pip or pipenv

# Add examples for fun
COPY examples /opt/mesa/examples

# Our "home" directory in the Docker image
WORKDIR /opt/mesa/mymodel

# Copy requirements.txt w/o code.  This layer is cached so we don't have to push every build
# NOTE: copy your model requirements.txt here
COPY examples/wolf_sheep/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
# pipenv LIES and does not sufficiently process requirements.txt
# and takes forever to do it.
# RUN pipenv install

# Copy rest of code so code changes only push the last layer
# NOTE: copy your model in here
COPY examples/wolf_sheep/ ./

# Run python
ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["run.py"]