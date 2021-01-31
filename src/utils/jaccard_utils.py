
import numpy as np
from gensim import corpora, matutils
from sklearn.metrics import pairwise_distances_chunked


def cleanse_histogram_counts(counts, n_docs):
    """Cleanses the histogram counts a symmetrical pairwise similarity matrix.
    This includes:
    1. Subtracting the 1-similarities on the matrix' diagonal.
    2. Dividing all counts by 2 (because of the symmetry).

    Args:
        counts (np.array): counts
        n_docs (int): number of documents

    Returns:
        np.array: cleansed counts
    """
    counts[-1] -= n_docs
    counts = counts / 2
    return counts.astype(int)

def chunked_jaccard_wrapper(doclist_X, doclist_Y=None):
    """Wrapper function for the chunked, parallelized jaccard similarity calculation.

    Args:
        doclist_X (list of strings): X - list of documents (words separated by empty space)
        doclist_Y (list of strings, optional): Y - list of documents. Defaults to None.

    Returns:
        tuple: (count, bins) histogram over all docs, as returned by `np.histogram`
    """
    mat_gen = pairwise_jaccard_distances(doclist_X, doclist_Y)
    glob_counts, glob_bins = np.histogram([], range=(0,1), bins=20)
    
    for dist_mat in mat_gen:
        # Convert from distance to similarity matrix chunk
        sim_mat = 1 - dist_mat
        counts, bins = np.histogram(sim_mat, bins=20, range=(0,1))
        glob_counts += counts

    if doclist_Y is None:
        glob_counts = cleanse_histogram_counts(glob_counts, len(doclist_X))
        
    return glob_counts, glob_bins


def pairwise_jaccard_distances(doclist_X, doclist_Y=None):
    """Calculates the matrix with the pairwise Jaccard *DISTANCES* matrix for one (or two) given document list(s).
    If `doclist_Y` is `None`, the matrix is created between every document of the `doclist_X`, else between `doclist_X` 
    and `doclist_Y`.

    Args:
        doclist_X (list of list of words): X - list of documents (words separated by empty space)
        doclist_Y (list of list of words, optional): Y - list of documents. Defaults to None.

    Returns:
        generator: generator of vertical chunks of the distance matrix
    """
    # Transform into sparse document-word-matrix
    wordlist_x = doclist_X
    wordlist_y = doclist_Y if doclist_Y is not None else []
    all_words = wordlist_x + wordlist_y

    # split into chunks
    lexicon = corpora.Dictionary()
    for index in range(0, len(all_words), 1000):
        lexicon.add_documents(all_words[index:index+1000])
        lexicon.filter_extremes(no_below=5, no_above=1, keep_n=None)

    bow_x = []
    for t in wordlist_x:
        bow_x.append(lexicon.doc2bow(t))

    vocab_matrix_x = matutils.corpus2dense(bow_x, num_terms=len(lexicon.token2id)).T.astype(bool)

    if doclist_Y is not None:
        bow_y = []
        for t in wordlist_y:
            bow_y.append(lexicon.doc2bow(t))
        vocab_matrix_y = matutils.corpus2dense(bow_y, num_terms=len(lexicon.token2id)).T
    else:
        vocab_matrix_y = None
    
    # Calculate jaccard *DISTANCES* (no similarities yet)
    matrix_gen = pairwise_distances_chunked(vocab_matrix_x, vocab_matrix_y, metric='jaccard', n_jobs=-1, working_memory=256)
    return matrix_gen