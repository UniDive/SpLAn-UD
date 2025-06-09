import sys
import csv
import grewpy as gp

gp.set_config("ud")

folder = sys.argv[1]

corpus_list = [x.strip() for x in open("corpus_list.txt", encoding="utf-8").readlines()]

corpora = {}

for corpus_id in corpus_list:
	corpora[corpus_id] = {"CORPUS": corpus_id}
	corpus = gp.Corpus(f"{folder}/{corpus_id}")
	corpora[corpus_id] = {"DATA": corpus}


# INTJ
request_str = "pattern { X[upos=INTJ] }"
request = gp.Request(request_str)
for corpus_id in corpora:
	corpus = corpora[corpus_id]["DATA"]
	occurrences = corpus.count(request, clustering_keys=["X.lemma"])

	if type(occurrences) == int:
		corpora[corpus_id]["CLUSTERS"] = 0
	else:
		corpora[corpus_id]["TOTAL COUNT"] = sum(occurrences.values())
		corpora[corpus_id]["CLUSTERS"] = len(occurrences)
		corpora[corpus_id]["VALUES"] = ", ".join(list(occurrences.keys()))

with open('tables/intj.csv', 'w') as csvfile:
	fieldnames = ['CORPUS', 'TOTAL COUNT', "CLUSTERS", "VALUES"]
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
						restval="_", extrasaction="ignore")

	writer.writeheader()
	for row in corpora:
		writer.writerow(dict[row])


# PUNCT
request_str = "pattern { X[upos=PUNCT] }"
request = gp.Request(request_str)

all_punct = set()
for corpus_id in corpus_list:
	corpus = corpora[corpus_id]["DATA"]
	occurrences = corpus.count(request, clustering_keys=["X.lemma"])

	if type(occurrences) == int:
		corpora[corpus_id]["CLUSTERS"] = 0
	else:
		corpora[corpus_id]["TOTAL COUNT"] = sum(occurrences.values())
		corpora[corpus_id]["CLUSTERS"] = len(occurrences)

		for x in occurrences:
			corpora[corpus_id][x] = occurrences[x]
			all_punct.add(x)

with open('tables/punct.csv', 'w') as csvfile:
	fieldnames = ['CORPUS', 'TOTAL COUNT', "CLUSTERS", "VALUES"] + list(all_punct)
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
						restval="_", extrasaction="ignore")

	writer.writeheader()
	for row in corpora:
		writer.writerow(corpora[row])


# INTERRUPT
request_str = 'pattern { X[form=re".+[-~]"] }'
request = gp.Request(request_str)

all_interrupt = set()

for corpus_id in corpus_list:
	corpus = corpora[corpus_id]["DATA"]
	occurrences = corpus.count(request, clustering_keys=["X.upos"])

	if type(occurrences) == int:
		corpora[corpus_id]["CLUSTERS"] = 0
	else:
		corpora[corpus_id]["TOTAL COUNT"] = sum(occurrences.values())
		corpora[corpus_id]["CLUSTERS"] = len(occurrences)

		for x in occurrences:
			corpora[corpus_id][x] = occurrences[x]
			all_punct.add(x)

with open('tables/interrupted.csv', 'w') as csvfile:
	fieldnames = ['CORPUS', 'TOTAL COUNT', "CLUSTERS", "VALUES"] + list(all_punct)
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval="_")

	writer.writeheader()
	for row in corpora:
		writer.writerow(corpora[row])