## Based on https://github.com/jupyter/docker-stacks/blob/master/scipy-notebook/Dockerfile
ARG BASE_CONTAINER=jupyter/minimal-notebook
# Link to base container: https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile
FROM $BASE_CONTAINER

USER root

# ffmpeg for matplotlib anim & dvipng+cm-super for latex labels
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg dvipng cm-super && \
        apt-get install -y graphviz && \
    rm -rf /var/lib/apt/lists/*
 

USER $NB_UID

COPY requirements.txt $HOME/work/requirements.txt
ADD setup.py $HOME/work/setup.py

WORKDIR $HOME/work
RUN pip3 install -r requirements.txt
