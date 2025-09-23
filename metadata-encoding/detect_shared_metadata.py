import sys
import os
import json
from conllup.conllup import readConlluFile, writeConlluFile

import pandas as pd
from itertools import combinations

in_folder = sys.argv[1]

# Process .conllu files
conllu_files = [f for f in os.listdir(in_folder) if f.endswith(".conllu")]
records = []
for sample in conllu_files:
	sample_id = os.path.splitext(sample)[0]

	try:
		conllu = readConlluFile(os.path.join(in_folder, sample))
		for sentence in conllu:
			metadata_dict = { "sample_id": sample_id }
			for key, value in sentence['metaJson'].items():
				if key not in ["sent_id", "global.columns"] and "text" not in key:
					metadata_dict[key] = value
			records.append(metadata_dict)
	except e:
		print(e)
		sys.exit(1)


df = pd.DataFrame(records)

# print (df)
# sys.exit(0)


def check_dep(key_a, key_b):
	# Create a mapping of key_a values to key_b values
	mapping = df.groupby(key_a)[key_b].unique().apply(set).to_dict()

	# Check if all values for key_a map to the same value for key_b
	if all(len(v) == 1 for v in mapping.values()):
		return mapping
	# else:
	# 	if key_a == "sample_id":
	# 		print(f"##################\nNo dep found: {key_a} -> {key_b}")
	# 		xxx = [v for v in mapping.values() if len(v) > 1]
	# 		print (xxx)

# Function to find dependencies
def find_dependencies(df):
	dependencies = {}
	equivalence = {}
	keys = df.columns.tolist()

	# Check all combinations of keys
	for key_a, key_b in combinations(keys, 2):
		mapping_ab = check_dep(key_a, key_b)
		mapping_ba = check_dep(key_b, key_a)
		if mapping_ab and mapping_ba:
			equivalence[(key_a, key_b)] = mapping_ab
		elif mapping_ab:
			dependencies[(key_a, key_b)] = mapping_ab
		elif mapping_ba:
			dependencies[(key_b, key_a)] = mapping_ba
	return equivalence, dependencies

# Find dependencies
equivalence, dependencies = find_dependencies(df)

# Print the results
for (key_a, key_b), mapping in equivalence.items():
	# print(f"===========\nEquivalence found: {key_a} <-> {key_b} with mapping: {mapping}")
	print(f" {key_a} <-> {key_b}")
for (key_a, key_b), mapping in dependencies.items():
	# print(f"===========\nDependency found: {key_a} -> {key_b} with mapping: {mapping}")
	print(f" {key_a} -> {key_b}")
