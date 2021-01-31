# IntrusionDetection

## Docker

We have created a docker image with the needed environment to run our system. 

### Docker Workflow

1. Build `Dockerfile` with

   ```bash
   docker build -t tristndev/datascience .
   ```

2. Start Docker container with docker compose

   ```
   docker-compose up
   ```

### Add Python packages

If additional Python packages are needed, simply add them to the `requirements.txt` and rebuild the Docker container. Make sure the changes of `requirements.txt` are reflected in the version control.

## Development Workflow with Jupyter Notebooks

As often done with data science or machine learning projects, we will use [Jupyter Notebooks](https://jupyter.org/) to interactively develop the components of the intrusion detection system.

We follow these conventions:

This notebook serves as a template notebook for us with some general remarks and explanations.

### Naming convention

For the notebooks, we use a naming convention that shows the owner and the order the analysis was done in: `<step>-<author>-<description>.ipynb` (e.g., `0.3-tristan-data_prep.ipynb`).

### Refactoring code

Whenever we need to refactor code originally written in a notebook (i.e., we need it in more than one notebook), we extract it into the `src` directory. In general, it is a good idea to 'refactor the good parts'. 
We import those files into the notebooks using the following preamble (see `blanko_notebook.ipynb`):

```{python}
import os, sys
PROJ_ROOT = os.path.join( os.pardir) # Depending on how deep the notebook is, might need to add more os.pardir
%load_ext autoreload # Make changes to the src code be seen immediately in the notebook
%autoreload 2

# Import into project
from src.data import packagename as dd
```





> The structure was initially based on the
> [cookiecutter data science](https://drivendata.github.io/cookiecutter-data-science/) structure.