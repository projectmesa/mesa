# We can't use slim because we need either git/wget/curl to
# download mesa-examples, and so installing them requires
# updating the system anyway.
FROM python:bookworm
LABEL maintainer="projectmesa maintainers@projectmesa.dev"

# To use this Dockerfile:
# 1. `docker build . -t mesa_image`
# 2. `docker run --name mesa_instance -p 8765:8765 -it mesa_image`
# 3. In your browser, visit http://127.0.0.1:8765
#
# Currently, this Dockerfile defaults to running the Schelling model, as an
# illustration. If you want to run a different example, simply change the
# MODEL_DIR variable below to point to another model, e.g.
# /mesa-examples/examples/sugarscape_cg or path to your custom model.
# You specify the MODEL_DIR (relative to this Git repo) by doing:
# `docker run --name mymesa_instance -p 8765:8765 -e MODEL_DIR=/mesa-examples/examples/sugarscape_cg -it mymesa_image`
# Note: the model directory MUST contain an app.py file.

ENV MODEL_DIR=/opt/mesa/mesa/examples/basic/schelling

# Don't buffer output:
# https://docs.python.org/3.10/using/cmdline.html?highlight=pythonunbuffered#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mesa

COPY . /opt/mesa

EXPOSE 8765/tcp

RUN pip3 install -e /opt/mesa[rec]

CMD ["sh", "-c", "cd $MODEL_DIR && solara run app.py --host=0.0.0.0"]

# To check file system:
# docker exec -it mesa_instance bash
