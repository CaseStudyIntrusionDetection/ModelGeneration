
# Readme

## Structure of config json file

* `general_setup`: General setup
  * `text_vars`: array of textual variables
  * `categ_vars`: array of categorical variables
  * `num_vars`: array of numerical variables
  * `bin_vars`: array of binary variables (1 or 0)
    * Possible header names: `["Accept", "Accept-Encoding", "Accept-Language", "Cache-Control", "Connection", "Content-Length", "Content-Type", "Cookie", "Host", "Origin", "Referer", "User-Agent"]`
  * `target_label`: target label to predict, e.g., one of `label, bin_label, data_tool`
* `nn_setup`: Neural net specific setup
  * `text`: Settings for **text input pipelines**
    * `max_features`: max vocab size
    * `max_len`: sequence length to pad outputs to
    * `embedding_dim`: dimensionality of embedding (output dims)
    * `layer_type`: used layer type, one of `['bi_rnn, cnn, rnn, gru]`
    * `n_units`: number of units in layer
    * `dropout`: dropout percentage in layer
  * `classifier`: Settings for **fully-connected classifier part**
    * `dropout`: dropout percentage after each layer
    * `n_layers`: number of layers
    * `n_units`: number of units per layer
  * `fitting`: Settings for **model training**/fitting
    * `early_stopping`: boolean to indicate whether to use an early stopping callback
    * `n_epochs`: number of (max) epochs in training
* `training_data`: Array of json file paths (in `data/raw/`) used for training
* `test_data`: Array of json files used for testing 

## Naming of config files
```
TRAIN-TEST-PREDICTIONSETTING-S-[RH]
```
* Train: Train data
* Test: Test data
* Predictionsetting: Attack Benign (ZAP vs. Selenium) or WW (with vs without zap-id)
* S: Single Request processing
* RH: Reduced Headers (removed the discriminant headers)

## Access the docker container

```
docker exec -it jupyter_notebook bash
```