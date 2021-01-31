import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, matutils
from sklearn.metrics import pairwise_distances


def jaccard_wrapper(doclist):
    """Wrapper function, that 1) calculates jaccard similarities and b) extracts all distances once.

    Args:
        doclist (list of strings): document list

    Returns:
        np.array: flat array of occurring jaccard values
    """
    # Transform into sparse document-word-matrix
    #vectorizer = CountVectorizer(token_pattern="(?u)[\w.!?\\/-]+")
    #vocab_matrix = vectorizer.fit_transform(doclist).todense()

    
    all_words = [x.split(" ") for x in doclist]
    lexicon = corpora.Dictionary(all_words)
    bow_x = []
    for t in all_words:
        bow_x.append(lexicon.doc2bow(t))
    vocab_matrix = matutils.corpus2dense(bow_x, num_terms=len(lexicon.token2id)).T.astype(bool)
    
    # Calculate jaccard similarities
    sim_matrix =  1 - pairwise_distances(vocab_matrix, metric='jaccard')
    
    # Extract values from upper triangle in matrix
    size = len(doclist)
    indices = np.triu_indices(size, k=1)
    flat_values = sim_matrix[indices]
    return flat_values
