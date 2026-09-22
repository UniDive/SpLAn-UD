"""
SCRIPT DESCRIPTION:
This script reorganizes CoNLL-U formatted linguistic data based on a JSON merge 
configuration file. It reads sentence and document data from individual .conllu files, 
then combines them into new output files according to the groupings specified in a 
`split.json` configuration file. This is used for creating the train/test/dev 
UD expected split.

If the file `metadata.json` is present in the `original_split` folder, it is taken into
account for producing the final split.

More info: https://grew.fr/spoken-language-guidelines/workgroups/spoken-data/treebank_structure.html

TODO:
 - add safety checks for unknown document_id or sent_id
 - add error in case of missing/duplicate sentences in the new corpora (check that the two "set of sent_ids" before/after merge is identical)
"""

import sys
import argparse
from pathlib import Path
import json
import glob
import os
from conllup.conllup import readConlluFile, writeConlluFile
from termcolor import colored, cprint

def load_json_file(json_file, required=True):
	try:
		with open(json_file, encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		if required:
			cprint(f"{json_file.name} not found in {json_file.parent}", "red")
			sys.exit(1)
		else:
			return ({})
	except json.JSONDecodeError as e:
		cprint(f"Error: Invalid JSON in {json_file.name}: {e}", "red")
		sys.exit(1)

def load_metadata(metadata_file):
	# Load shared metadata
	try:
		with open(metadata_file, encoding="utf-8") as meta_file:
			return json.load(meta_file)
	except FileNotFoundError:
		cprint(f"No metadata.json not found in {in_folder}", "blue")
		return
	except json.JSONDecodeError as e:
		cprint(f"Error: Invalid JSON in metadata.json: {e}", "red")
		sys.exit(1)

def expand(shared_meta, document_id, conllu):
	"""Restore document-specific and derived metadata to a sentence."""
	meta = conllu['metaJson']

	# Add document-specific metadata
	document_meta = shared_meta.get('document_id', {}).get(document_id, {})
	meta.update(document_meta)

	# Add derived metadata based on current metadata values
	for key, value in list(meta.items()):
		if key in shared_meta and value in shared_meta[key]:
			meta.update(shared_meta[key][value])

def run_merge(base_folder):
	"""
	Main function that orchestrates the corpus merging process.
	
	Args:
		base_folder (str): Path to the base folder containing an 'original_split' 
						  subdirectory with .conlu files and a merge.json config file.
	"""
	
	base_path = Path(base_folder)

	# Define the path to the folder containing original CoNLL-U files and merge configuration
	original_split_folder = base_path / "not-to-release" / "original_split"

	# Load the merge configuration JSON file that defines how to group documents/sentences
	json_merge = load_json_file(original_split_folder / "merge.json")

	shared_meta = load_json_file(original_split_folder / "metadata.json", required=False)
	if shared_meta is None: shared_meta = dict()

	# Initialize lists to store IDs of documents and sentences that need to be included
	needed_document_ids = []
	needed_sent_ids = []
	
	# Parse the merge.json to extract all document IDs and sentence IDs referenced
	for (_, section_list) in json_merge.items():
		for section in section_list:
			if "document_ids" in section:
				needed_document_ids += section["document_ids"]
			if "sent_ids" in section:
				needed_sent_ids += section["sent_ids"]

	# Initialize dictionaries to cache loaded documents and sentences
	document_dict = dict()
	sent_dict = dict()

	# Get a list of all .conllu files in the original_split folder
	document_file_list = sorted(original_split_folder.glob("*.conllu"))

	# Load CoNLL-U data from all files and organize by document or sentence ID
	for document_file in document_file_list:
		# Read the CoNLL-U file
		document = readConlluFile(document_file)
		
		# Remove unnecessary metadata column information
		del document[0]['metaJson']['global.columns']
		
		# Extract the document ID from the filename (without extension)
		document_id = document_file.stem
		
		# If this document is needed as a whole, store it in the document dictionary
		if document_id in needed_document_ids:
			for sentence in document:
				expand(shared_meta, document_id, sentence)
			document_dict[document_id] = document
		else:
			# Otherwise, extract individual sentences and store them by sentence ID
			for sentence in document:
				sent_id = sentence['metaJson']['sent_id']
				expand(shared_meta, document_id, sentence)
				sent_dict[sent_id] = sentence

	# Build output files according to the merge configuration
	for (output_file, section_list) in json_merge.items():
		output_corpus = []
		
		# Add documents and sentences to the output corpus based on the configuration
		for section in section_list:
			# Add all sentences from specified documents
			if "document_ids" in section:
				for document_id in section["document_ids"]:
					output_corpus.extend(document_dict[document_id])
			
			# Add individually specified sentences
			if "sent_ids" in section:
				output_corpus.extend([sent_dict[sent_id] for sent_id in section["sent_ids"]])
		
		# Write the assembled corpus to a new .conllu file
		writeConlluFile(
			f"{os.path.join(base_folder, output_file)}.conllu",
			output_corpus,
			overwrite=True
		)
	cprint(f"Successfully merge {len(document_file_list)} documents to {len(json_merge)} files", "green")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='''Build the .conllu file at the root of `base_folder` from data available in subfolder `original_split`.
Requirements: the folder `original_split` must contain a file `merge.json` as explained **TODO LINK**
Optional: if the folder `original_split` contains a file `metadata.json`, it is taken into account in the production of final files.
WARNING: existing .conllu files in `base_folder` will be overwritten''',
    formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument(
		"base_folder",
		help="Path to the folder containing the treebank"
	)

	args = parser.parse_args()

	run_merge(args.base_folder)
