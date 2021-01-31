import sys
import json

import src.data.make_datasets_lda 
import src.visualization.visualize_lda_corpus 

# Settings object for defining all kinds of parameters in one place. Using separate
# settings files, we can run multiple pipelines in parallel (e.g., we can specify different
# input and output files such that conflicts are avoided).
corpus_settings = json.load(open(sys.argv[1], 'r'))
# make sure to divide path for outputs
if corpus_settings['output']['dir'][-1] != '/':
	corpus_settings['output']['dir'] += '/'


for dataset in corpus_settings['datasets']:
	settings = {
		'corpus' : {
			'use_times' : False,
			'document_per_request' : True,
			'document_per_connection_id' : False,
			'document_request_window_size' : 0
		},
		'training_data' : dataset['training_data'],
		'test_data' : dataset['test_data'],
		'output' : {
			'dir' : corpus_settings['output']['dir'],
			'name' : corpus_settings['output']['name']
		}
	}

	print('Started:', dataset['outname'])

	src.data.make_datasets_lda.main(settings)
	rcode = src.visualization.visualize_lda_corpus.main(settings,
		numpy_rounds=corpus_settings['rounds'], numpy_chunksize=corpus_settings['chunksize'], numpy_steps=corpus_settings['steps'])

	f = open(corpus_settings['output']['dir'] + 'viz/' + dataset['outname'] + '.R', "w+")
	f.write(rcode)
	f.close()