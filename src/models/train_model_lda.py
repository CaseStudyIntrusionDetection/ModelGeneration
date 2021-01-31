import gensim 
import json

from src.utils.float_encoder import FloatEncoder 

def learn_lda_model(settings):
	"""Learns the LDA model.

	Args:
		settings (dict): The settings object for all kinds of parameters (including
		the hyperparameters for the LDA model).

	Returns:
		(numpy.ndarray, array of dict): The learned LDA model and the bag of words corpus.
	"""

	# load corpus (as bow) and dictionary
	corpus = json.load(open(settings['output']['dir'] + 'temp/' + settings['output']['name'] + '_bow.json', 'r'))
	dict = gensim.corpora.Dictionary.load(settings['output']['dir'] + 'temp/' + settings['output']['name'] + '.dict')

	# prepare bag of words
	bow = [d['bow'] for d in corpus]

	# learn model
	model = gensim.models.LdaMulticore(
		corpus=bow,
		num_topics=settings['lda']['topics'],
		id2word=dict,
		passes=2,
		workers=6,
		per_word_topics=True,
		alpha=settings['lda']['alpha'],
		eta=settings['lda']['beta'],
		minimum_phi_value=settings['lda']['min_phi_value'],
		iterations=settings['lda']['max_iteration'],
		minimum_probability=settings['lda']['min_probability'],
		gamma_threshold=settings['lda']['gamma_threshold']
	)

	model.save(settings['output']['dir'] + 'temp/' + settings['output']['name'] + '.ldamodel')

	return model, corpus

'''
	SUPERVISED TOPIC to Attack Type/ Emulator mapping
'''

def model_stats(settings, model, corpus):
	"""Computes statistics (like perplexity) for a given LDA model.

	Args:
		settings (dict): The settings object for all kinds of parameters.
		model (numpy.ndarray): The LDA model to compute statistics for.
		corpus (array of dict): The bag of words corpus.

	Returns:
		(dict, float): A dictionary containing a key for each topic with the most
		probable words for that topic as a value; and the perplexity of the model.
	"""

	topics = {}
	# get topics and most probable words and their probability
	for topic in model.show_topics(num_topics=settings['lda']['topics'], num_words=15, formatted=False):
		topics[topic[0]] = {}
		for word,prob in topic[1]:
			# propability per top 15 words in topic
			topics[topic[0]][word] = prob

	# model perplexity
	perplexity = -1 * model.log_perplexity([d['bow'] for d in corpus])

	return topics, perplexity

def get_document_topics(settings, model, corpus):
	"""Assigns each document a sorted list of topics such that the most
	probable topics are first.

	Args:
		settings (dict): The settings object for all kinds of parameters.
		model (numpy.ndarray): The LDA model to compute statistics for.
		corpus (array of dict): The bag of words corpus.

	Returns:
		(array of dict): A dictionary object for each document in the corpus
		which contains the document information, including the list of sorted topics.
	"""

	result = []
	for d in corpus:
		# get topics per document 
		topics = model.get_document_topics(d['bow'], minimum_probability=settings['lda']['min_probability'], minimum_phi_value=settings['lda']['min_phi_value'], per_word_topics=False)
		# log (sorted) topics per document to file
		topics.sort(key=lambda t: t[1], reverse=True)
		# add top-topics per document
		result.append({
			"corpus" : d['corpus'],
			"type" : d['type'],
			"emulator" : d['emulator'],
			"perplexity" : -1 * model.log_perplexity([d['bow']]),
			"topics" : topics
		})

	return result

def get_topics_for_class(settings, model, corpus, class_type, single_value_class=True):
	"""Determines the probabilities for the topics for a given class type.

	Args:
		settings (dict): The settings object for all kinds of parameters.
		model (numpy.ndarray): The LDA model to compute statistics for.
		corpus (array of dict): The bag of words corpus.
		class_type (str): The name of the class type key.
		single_value_class (bool, optional): Indicates whether the key class_type has a single
		value (True) or a list of values (False). Defaults to True.

	Returns:
		(dict): A dictionary with a key for each class (e.g. for each used emulator or for
		each type like attack/benign) and the corresponding topic probability distribution
		for this class.
	"""
	result = {}

	for d in corpus:
		topics = model.get_document_topics(d['bow'], minimum_probability=settings['lda']['min_probability'], minimum_phi_value=settings['lda']['min_phi_value'], per_word_topics=False)

		if single_value_class:
			# add the type (e.g. attack, benign) and set all topics to prob 0
			if d[class_type] not in result:
				result[d[class_type]] = [0 for _ in range(settings['lda']['topics'])]
		else:
			# add the emulator and set all topics to prob 0 (multiple emulators possible, separated by ' ')
			for e in d[class_type].split(' '):
				e = e.strip()
				if len(e) > 0 and e not in result:
					result[e] = [0 for _ in range(settings['lda']['topics'])]

		# for each topic of document
		for tid, prob in topics:
			if single_value_class:
				# add the probability of topic to the types topic(-distribution)
				result[d[class_type]][tid] += prob

			else:
				# add the probability of topic to the emulators topic(-distribution)
				for e in d[class_type].split(' '):
					e = e.strip()
					if len(e) > 0:
						result[e][tid] += prob

	# normalize topic distributions
	for distType in result.keys():
		distSum = sum(result[distType])
		result[distType] = [prob/distSum for prob in result[distType]]

	return result

def main(settings):
	# generate/ load model
	model, corpus = learn_lda_model(settings)

	# collect stats
	topic, perplexity = model_stats(settings, model, corpus)

	# results
	result = {
		'topic' : topic, # each topic by most probable words
		'perplexity' : perplexity,
		'requestTopics' : {
			'emulators' : get_topics_for_class(settings, model, corpus, 'emulator', single_value_class=False), # the topics per used emulator (none, rfi, ...)
			'types' : get_topics_for_class(settings, model, corpus, 'type'), # the topics per type (benign, attack)
			'zap-ids' : get_topics_for_class(settings, model, corpus, 'zap-id', single_value_class=False)
		}
	}

	# add for each document, if active
	if settings['corpus']['output_document_topics']:
		result['documents'] = get_document_topics(settings, model, corpus)

	f = open(settings['output']['dir'] + 'lda_trained/' + settings['output']['name'] + '_trained.json', "w+")
	f.write(json.dumps(result, indent=4, sort_keys=False, cls=FloatEncoder))
	f.close()