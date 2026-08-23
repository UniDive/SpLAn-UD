import sys
import argparse
from pathlib import Path
import json
from conllup.conllup import readConlluFile, writeConlluFile
from termcolor import colored, cprint

import pandas as pd
from itertools import combinations

def process(in_folder, keys_to_ignore):
	"""Process all .conllu files and extract shared metadata."""

	def is_ignored(key):
		if key in ["sent_id", "global.columns"]:
			return True
		if key.startswith("text"):
			return True
		if key in keys_to_ignore:
			return True
		else:
			return False

	in_path = Path(in_folder)

	if not in_path.is_dir():
		cprint(f"Error: '{in_folder}' is not a valid directory", "red")
		sys.exit(1)

	# Process .conllu files
	conllu_files = sorted(in_path.glob("*.conllu"))
	records = []
	for conllu_file in conllu_files:
		document_id = conllu_file.stem

		try:
			conllu = readConlluFile(conllu_file)
			for sentence in conllu:
				metadata_dict = { "document_id": document_id }
				for key, value in sentence['metaJson'].items():
					if not is_ignored(key):
						metadata_dict[key] = value
				records.append(metadata_dict)
		except Exception as e:
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

def output_text(equivalence, dependencies):
	"""Output results in text format (default)."""
	cprint(f"Equivalences: {len(equivalence)}", "green")
	cprint(f"Dependencies: {len(dependencies)}", "green")
	for (key_a, key_b), mapping in equivalence.items():
		print(f" {key_a} <-> {key_b}")
	for (key_a, key_b), mapping in dependencies.items():
		print(f" {key_a} -> {key_b}")

def output_dot(equivalence, dependencies):
	"""Output results in Graphviz DOT format."""
	print("digraph metadata_dependencies {")
	print("  rankdir=LR;")
	print("  node [shape=box];")
	for (key_a, key_b), mapping in equivalence.items():
		print(f'  "{key_a}" -> "{key_b}" [dir=both];')
	for (key_a, key_b), mapping in dependencies.items():
		print(f'  "{key_a}" -> "{key_b}"')
	print("}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='Process .conllu files and extract "shareable" metadata dependencies.',
    formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument(
		"in_folder",
		help="Path to the folder containing .conllu files"
	)
	parser.add_argument(
		"--ignore-keys",
		nargs="+",
		default=[],
		help="""Metadata `sent_id` and keys starting by `text` are ignored by default.
You can provide additional metadata keys to ignore during processing (default: None)"""
	)
	parser.add_argument(
		"--output-format",
		choices=["dot", "text"],
		default="text",
		help="Output format (default: text)"
	)

	args = parser.parse_args()

	equivalence, dependencies = process(args.in_folder, args.ignore_keys)

	if args.output_format == "dot":
		output_dot(equivalence, dependencies)
	else:  # text
		output_text(equivalence, dependencies)
