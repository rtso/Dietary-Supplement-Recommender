import metapy

idx = metapy.index.make_inverted_index('config.toml')
ranker = metapy.index.DirichletPrior()
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
        print(str(i + 1) + ': ' + str(supplements[doc[0]]))
    print()

ev = metapy.index.IREval('config.toml')

num_results = 10
with open('queries.txt') as query_file:
    for query_num, line in enumerate(query_file):
        query.content(line.strip())
        results = ranker.score(idx, query, num_results)
        avg_p = ev.avg_p(results, query_num, num_results)
        print("Query {} average precision: {}".format(query_num + 1, avg_p))

print(ev.map())