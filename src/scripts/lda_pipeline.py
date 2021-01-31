import sys
import json
import time

# Settings object for defining all kinds of parameters in one place. Using separate
# settings files, we can run multiple pipelines in parallel (e.g., we can specify different
# input and output files such that conflicts are avoided).
settings = json.load(open(sys.argv[1], 'r'))
# make sure to divide path for outputs
if settings['output']['dir'][-1] != '/':
	settings['output']['dir'] += '/'

#####

start_time_train = time.time()

if settings['pipeline_active']['dataset']:
	print('Running Data Processing')
	import src.data.make_datasets_lda 
	src.data.make_datasets_lda.main(settings)

if settings['pipeline_active']['visualize_dataset']:
	print("Visualizing dataset")
	import src.visualization.visualize_lda_corpus 
	print(src.visualization.visualize_lda_corpus.main(settings))

if settings['pipeline_active']['features']:
	print('Running Corpus Feature Extraction')
	import src.features.build_features_lda
	src.features.build_features_lda.main(settings)

if settings['pipeline_active']['train']:
	print("Learning LDA Model and Topic Distributions per Request Type")
	import src.models.train_model_lda
	src.models.train_model_lda.main(settings)

train_time = time.time() - start_time_train
start_time_test = time.time()

if settings['pipeline_active']['predict']:
	print("Predicting data")
	import src.models.predict_model_lda
	src.models.predict_model_lda.main(settings)

test_time = time.time() - start_time_test

if settings['pipeline_active']['visualize']:
	print("Visualizing lda model")
	import src.visualization.visualize_lda
	src.visualization.visualize_lda.main(settings)


print("Timing – Training:", train_time, "; Testing:", test_time)