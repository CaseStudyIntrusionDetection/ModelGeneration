import json
import numpy
import random
import re
import concurrent.futures
import math

from src.utils.jaccard_utils import chunked_jaccard_wrapper 

word_id_map = {} # Maps each word to a unique id (index)
word_id_max = 0 # Keeps track of the next free id

def get_word_id_array(d):
	global word_id_map, word_id_max
	""" This function is used to gather all words appearing in the corpus.
	Therefore assign a unique id for each word occuring in the corpus and add
	the id to the list of all possible words in the corpus. However this
	function is only applied to a single document. 
		
		Args: d (dict): The document.

		Returns:
			(array): An array containing the ids for all possible words.
	"""

	idlist = []
	for word in words_from_doc(d):
		if re.match(r'^[a-f0-9]{128}$', word) == None:
			if word not in word_id_map:
				word_id_map[word] = word_id_max
				word_id_max += 1
				
			idlist.append(word_id_map[word])
	return idlist

def words_from_doc(d):
	"""Returns all words from a given document.

		Args:
			d (dict): The document.

		Returns:
			(iterable): The words of the given document.
	"""
	return filter(lambda t: len(t.strip()) > 0, d['document'].split(' ')) 

def get_vocab_matrix(wordlist):
	""" Create a matrix with #documentsPerCorpus rows and #wordsPerCorpus columns. 
		For each document we mark each column/each word which occurs in the specific document.

		Args:
			wordlist (array): List of all word id lists for all documents.

		Returns:
			(numpy.ndarray): A matrix representing which word occurs in which document.
	"""
	vocab_matrix = numpy.zeros(shape=(len(wordlist), word_id_max), dtype=numpy.bool_)
	for d_i,words in enumerate(wordlist):
		for word in words:
			vocab_matrix[d_i][word] = True

	return vocab_matrix

def get_as_R(*rows):
	"""Converts histograms into R code for plotting the histograms.

		Args:
			*rows (array): Arbitrary many histograms.

		Returns:
			(str): R code to plot the histograms.
	"""
	R = "par(mfrow=c("+ str(len(rows)) +",1))\n"
	for row in rows:
		R += "barplot(c(" + ', '.join([str(v) for v in row]) + "))\n"
	return R

def jaccard_self(vocab_array, chunksize, steps):
	"""Computes the Jaccard coefficients for a single matrix.

		Args:
			vocab_array (list list of ints): List of word ids per document
			chunksize (int, optional): Size per chunk drawn to calculate histogram
			steps (int, optional): Number of bars in the histogram.

		Returns:
			(array): The histogram containing frequencies of the Jaccard coefficients for
			the given matrix.
	"""

	random.shuffle(vocab_array)
	middle = len(vocab_array) // 2
	
	return jaccard_other(vocab_array[:middle], vocab_array[middle:], chunksize, steps)

def jaccard_other(vocab_a, vocab_b, chunksize, steps):
	"""Computes the Jaccard coefficients for two given matrices.

		Args:
			vocab_a (list list of ints): List of word ids per document
			vocab_b (list list of ints): List of word ids per document
			chunksize (int, optional): Size per chunk drawn to calculate histogram
			steps (int, optional): Number of bars in the histogram.

		Returns:
			(array): The histogram containing frequencies of the Jaccard coefficients for
			the given matrix.
	"""
	hist = numpy.zeros(steps+1, dtype=int)

	random.shuffle(vocab_b)
	random.shuffle(vocab_a)

	for index in range(0, min(len(vocab_b), len(vocab_a)), chunksize):
		vocab_b_chunk = get_vocab_matrix(vocab_b[index:index+chunksize])
		vocab_a_chunk = get_vocab_matrix(vocab_a[index:index+chunksize])
		for d_i in range(len(vocab_b_chunk)):
			# compute the union and intersection for the current document and all documents below the diagonal matrix
			union = numpy.logical_or(vocab_a_chunk, vocab_b_chunk[d_i], dtype=numpy.bool_)
			intersection = numpy.logical_and(vocab_a_chunk, vocab_b_chunk[d_i], dtype=numpy.bool_)

			# count how many 1 we have in our union and intersection
			union_c = numpy.count_nonzero(union, axis=1)
			intersection_c = numpy.count_nonzero(intersection, axis=1)

			# compute the jaccard coefficient as #intersections / #unions 
			jaccard_values = numpy.around( ( intersection_c / union_c ) * steps ).astype(int)

			#add occurrences to histogram
			j_values, j_counts = numpy.unique(jaccard_values, return_counts=True)
			for v,c in zip(j_values, j_counts):
				hist[v] += c

	return hist

def main(settings, numpy_rounds=10, numpy_chunksize=1000, numpy_steps=20, worker_count=4):
	global word_id_map, word_id_max

	word_id_map = {} # Maps each word to a unique id (index)
	word_id_max = 0 # Keeps track of the next free id
	
	#main_sklearn_approach(settings)
	return main_numpy_approach(settings, numpy_rounds, numpy_chunksize, numpy_steps, worker_count)

def main_sklearn_approach(settings):
	# load the two corpora for which we want to compute the jaccard coefficient
	corpus_a = json.load(open(settings['output']['dir'] + 'processed/' + settings['output']['name'] + '_trainset.json', 'r'))
	corpus_b = json.load(open(settings['output']['dir'] + 'processed/' + settings['output']['name'] + '_testset.json', 'r'))

	doclist_a = [ list(words_from_doc(d)) for d in corpus_a ]
	doclist_b = [ list(words_from_doc(d)) for d in corpus_b ]
	
	print('a')
	a, _ = list(chunked_jaccard_wrapper(doclist_a))
	print('b')
	b, _ = list(chunked_jaccard_wrapper(doclist_b))
	print('ab')
	ab, _ = list(chunked_jaccard_wrapper(doclist_a, doclist_b))

	print(get_as_R(a, b, ab))

def main_numpy_approach(settings, numpy_rounds, numpy_chunksize, numpy_steps, worker_count):
	global word_id_map
	# load the two corpora for which we want to compute the jaccard coefficient
	corpus_a = json.load(open(settings['output']['dir'] + 'processed/' + settings['output']['name'] + '_trainset.json', 'r'))
	corpus_b = json.load(open(settings['output']['dir'] + 'processed/' + settings['output']['name'] + '_testset.json', 'r'))

	# identify all words use in the first corpus
	wordlist_a = []
	for d in corpus_a:
		wordlist_a.append(get_word_id_array(d))

	# identify all words use in the second corpus
	wordlist_b = []
	for d in corpus_b:
		wordlist_b.append(get_word_id_array(d))

	# free some memory
	word_id_map, corpus_a, corpus_b = {}, 0, 0

	# empty histograms
	a = numpy.zeros(numpy_steps+1, dtype=int)
	b = numpy.zeros(numpy_steps+1, dtype=int)
	ab = numpy.zeros(numpy_steps+1, dtype=int)

	# run each multiple times
	with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
		
		count = 0
		for _ in range(math.ceil(numpy_rounds / worker_count)):
			# schedule threads
			threads = []
			for _ in range(worker_count):
				if count < numpy_rounds:
					print('Start Trainset:', count)
					threads.append( executor.submit(jaccard_self, wordlist_a.copy(), chunksize=numpy_chunksize, steps=numpy_steps) ) # pos Argumente / pos/benannte * benannt
					count += 1

			# collect results
			for thread in threads:
				a += thread.result()

		print('Finished a')

		count = 0
		for _ in range(math.ceil(numpy_rounds / worker_count)):
			threads = []
			for _ in range(worker_count):
				if count < numpy_rounds:
					print('Start Testset:', count)
					threads.append( executor.submit(jaccard_self, wordlist_b.copy(), chunksize=numpy_chunksize, steps=numpy_steps) ) # pos Argumente / pos/benannte * benannt
					count += 1

			# collect results
			for thread in threads:
				b += thread.result()

		print('Finished b')

		count = 0
		for _ in range(math.ceil(numpy_rounds / worker_count)):
			threads = []
			for _ in range(worker_count):
				if count < numpy_rounds:
					print('Start Train- & Testset:', count)
					threads.append( executor.submit(jaccard_other, wordlist_a.copy(), wordlist_b.copy(), chunksize=numpy_chunksize, steps=numpy_steps) ) # pos Argumente / pos/benannte * benannt
					count += 1

			# collect results
			for thread in threads:
				ab += thread.result()

		print('Finished ab')

	# normalize
	a = list(a / a.max())
	b = list(b / b.max())
	ab = list(ab / ab.max())
	
	# return as R-Code
	return get_as_R(a, b, ab)