import sys
import os
import json
from conllup.conllup import readConlluFile, writeConlluFile
from termcolor import colored, cprint

import pandas as pd
from itertools import combinations

def process (in_folder):

	# Process .conllu files
	conllu_files = [f for f in os.listdir(in_folder) if f.endswith(".conllu")]
	records = []
	for sample in conllu_files:
		document_id = os.path.splitext(sample)[0]

		try:
			conllu = readConlluFile(os.path.join(in_folder, sample))
			for sentence in conllu:
				metadata_dict = { "document_id": document_id }
				for key, value in sentence['metaJson'].items():
					if key not in ["sent_id", "global.columns", "old_id"] and "text" not in key:
						metadata_dict[key] = value
				records.append(metadata_dict)
		except e:
			print(e)
			sys.exit(1)


	df = pd.DataFrame(records)

	def check_dep(key_a, key_b):
		# Create a mapping of key_a values to key_b values
		mapping = df.groupby(key_a)[key_b].unique().apply(set).to_dict()

		# Check if all values for key_a map to the same value for key_b
		if all(len(v) == 1 for v in mapping.values()):
			return mapping

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

	return find_dependencies(df)

if __name__ == "__main__":
	if len(sys.argv) == 2:
		in_folder = sys.argv[1]
		equivalence, dependencies = process(in_folder)
		cprint (f"Equivalences: {len(equivalence)}", "green")
		cprint (f"Dependencies: {len(dependencies)}", "green")
		for (key_a, key_b), mapping in equivalence.items():
			print(f" {key_a} <-> {key_b}")
		for (key_a, key_b), mapping in dependencies.items():
			print(f" {key_a} -> {key_b}")

	else:
		cprint("Usage: python metadata_detect_sharable.py <in_folder>", "red")
		sys.exit(1)
