import metapy

idx = metapy.index.make_inverted_index('config.toml')
ranker = metapy.index.OkapiBM25()
queries = []
query_fd = open('../queries_2.txt','r')
queries = query_fd.read().split('\n')[0:-1]
query_fd.close()
supplements_fd = open('../supplements_list.txt','r')
supplements = supplements_fd.read().split('\n')[0:-1]
supplements_fd.close()
for q in queries:
    print(q)
    query = metapy.index.Document()
    query.content(q)
    top_docs = ranker.score(idx, query, num_results=5)
    for i, doc in enumerate(top_docs):
        print(str(i + 1) + ': ' + str(supplements[doc[0]]) + ' ', end='')
    print()
    print()