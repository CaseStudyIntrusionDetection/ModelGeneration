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

#Installing python packages 
RUN pip3 install widgetsnbextension && \
    jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    # Also activate ipywidgets extension for JupyterLab
    # Check this URL for most recent compatibilities
    # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
    jupyter labextension install @jupyter-widgets/jupyterlab-manager@^2.0.0 --no-build && \
    jupyter labextension install @bokeh/jupyter_bokeh@^2.0.0 --no-build && \
    jupyter labextension install jupyter-matplotlib@^0.7.2 --no-build && \
    npm cache clean --force && \
    rm -rf "/home/${NB_USER}/.cache/yarn" && \
    rm -rf "/home/${NB_USER}/.node-gyp" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"