# Model Generation

## General
The `data` folder contains the data to train the model on.

## Topic Modeling
The scripts to train and evaluate a topic model can be found in `lda`.
Start the Docker container via `lda/run.sh` and afterwards start the
pipeline via `scripts/run.sh`.

## Neural Networks
The scripts to train and evaluate a neural network can be found in `nn`.
Start the Docker container via `docker-compose up` in the projects root
and afterwards a shell via `docker exec -it jupyter_notebook sh`. Then 
start the pipeline via `cd nn && sh ./run.sh`.

**Attention:** The example datasets are too small, thus the NN pipeline will fail. 

> All code runs in Docker containers.

## License
All components are licensed under
[GPLv3 License](https://github.com/CaseStudyIntrusionDetection/ModelGeneration/blob/master/LICENSE).


```
Model Generation for the CaseStudy IntrusionDetection
Copyright (C) 2021 CaseStudy IntrusionDetection Developers

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

> The structure was initially based on the
> [cookiecutter data science](https://drivendata.github.io/cookiecutter-data-science/) structure.