import json

def generate_data(settings, prediction, topK):
	"""Generates the most probable classes for each topic and the most
	probable topics for each class.

	Args:
		settings (dict): The settings object for all kinds of parameters.
		prediction (dict): The probability distributions for each topic and each class.
		topK (int): Specifies how many of the top values should be considered.

	Returns:
		(array of array, dict): An array containing the most probable
		classes for each topic at the topic number's index and a dictionary
		containing the most probable topics for each class.
	"""
	topic_classes = [[] for _ in range(settings['lda']['topics'])]
	class_topics = {}

	for class_type in prediction['requestTopics']:
		class_topics[class_type] = {}
		for name,topic_dist in prediction['requestTopics'][class_type].items():
			topic_dist = list(enumerate(topic_dist))
			topic_dist.sort(key=lambda t: t[1], reverse=True)
			class_topics[class_type][name] = {}
			for topic,prob in topic_dist[:topK]:
				if prob > 0:
					if name not in topic_classes[topic]:
						topic_classes[topic].append(name)
					class_topics[class_type][name][topic] = prob

	return topic_classes, class_topics

def print_t_c(topic_classes):
	"""Prints the most probable classes per topic.

		Args:
			topic_classes (array of array): An array containing the most probable
			classes for each topic at the topic number's index.
	"""
	print("Most probable classes per topic")
	for topic,classes in enumerate(topic_classes):
		if len(classes) > 0:
			print("\t", str(topic).rjust(3), ', '.join(sorted(classes)) )
		
def print_t_c_cluster(topic_classes):
	"""Prints cluster of similar topics in order to visualize which topics are
	close to each other.

		Args:
			topic_classes (array of array): An array containing the most probable
			classes for each topic at the topic number's index.

		Returns:
			(array): An array containing tuples of similar topics.
	"""

	def intersection(a,b):
		"""Computes the intersection of two sets a and b.

		Args:
			a (array): The first set.
			b (array): The second set.

		Returns:
			(array): The intersection of a and b.
		"""
		return list(set(a) & set(b))

	max_intersection = -1
	intersection_map = [[0 for _ in range(len(topic_classes))] for _ in range(len(topic_classes))]
	intersection_values = [[[] for _ in range(len(topic_classes))] for _ in range(len(topic_classes))]
	for topicA,classesA in enumerate(topic_classes):
		for topicB,classesB in enumerate(topic_classes):
			inter = intersection(classesA,classesB)
			intersection_map[topicA][topicB] = len(inter)
			intersection_values[topicA][topicB] = inter
			if max_intersection < intersection_map[topicA][topicB]:
				max_intersection = intersection_map[topicA][topicB]

	if max_intersection > 0:
		intersection_map = [[e/max_intersection for e in l] for l in intersection_map]

	topics_done = [len(classes) == 0 for classes in topic_classes] # only consider topic which habe most prob. classes
	cluster = []
	for topicA,similarities in enumerate(intersection_map):
		if not topics_done[topicA]:
			similars = [topicA]
			inters = []
			topics_done[topicA] = True
			for topicB,similarity in enumerate(similarities):
				if topicA != topicB and similarity > 0.3:
					similars.append(topicB)
					inters.extend(intersection_values[topicA][topicB])
					topics_done[topicB] = True
			cluster.append((similars, set(inters)))
	
	print("Groups/ cluster of similar topics")
	for tops,ints in cluster:
		print("\t", ', '.join([str(t) for t in tops]))
		print("\t\t", ', '.join(ints))
	
	return cluster

def print_c_t(class_topics):
	"""Prints the most probable topics for each class.

		Args:
			class_topics (dict): A dictionary containing the most probable
			topics for each class.
	"""
	print("Most probable topic for each class")
	for class_type in class_topics:
		print("\t", class_type)
		for name,topics in class_topics[class_type].items():
			print("\t\t", name)
			for topic,prob in topics.items():
				print("\t\t\t", str(topic).rjust(3), prob)

def print_topic_words(trained, topic_sets, topK):
	"""Prints the most probable words for each topic cluster.

		Args:
			trained (dict): The probability distributions for each topic and each class.
			topic_sets (array): The topic clusters.
			topK (int): Specifies how many of the top values should be considered.
	"""
	print("Most probable words per topic cluster")
	for topic_set in topic_sets:
		words = {}
		for topic in topic_set:
			for word, prob in trained['topic'][str(topic)].items():
				if word in words:
					words[word] += prob
				else:
					words[word] = prob
		words = [(word, prob) for word, prob in words.items()]
		words.sort(key=lambda t: t[1], reverse=True)
		
		print("\t","Cluster topics:", topic_set)
		for word,prob in words[:topK]:
			print("\t\t", word)

def main(settings):
	trained = json.load(open(settings['output']['dir'] + 'lda_trained/' + settings['output']['name'] + '_trained.json', 'r'))
	topic_classes, class_topics = generate_data(settings, trained, topK=3)

	print_t_c(topic_classes)
	print("")
	cluster = print_t_c_cluster(topic_classes)
	print("")
	print_topic_words(trained, [ c[0] for c in cluster ], topK=5)
	print("")
	print_c_t(class_topics)