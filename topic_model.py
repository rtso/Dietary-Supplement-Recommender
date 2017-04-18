import em_clustering as em
import numpy as np
from sklearn.cluster import KMeans

np.set_printoptions(threshold=np.nan)

k = 30
with open('docword.nips.txt', 'r') as file:
    N = int(file.readline())
    V = int(file.readline())
    nnz = int(file.readline())
    data = np.zeros((N, V))
    for line in file:
        line = line.split()
        doc_id = int(line[0])
        term_id = int(line[1])
        count = int(line[2])
        data[doc_id - 1, term_id - 1] = count
    data += 1


def topic_model_em():
    output = em.cluster_em(data, k, mode='Topic', batch_size=2000, tolerance=100, max_iter=500, verbose=True)
    centroids = output['p']
    topics = output['pi']
    top = list()
    print(topics)
    for i in range(k):
        top.append(centroids[i].argsort()[-10:])

    np.savetxt('topic-prob.txt', topics)
    np.savetxt('top-words.txt', top)

topic_model_em()

