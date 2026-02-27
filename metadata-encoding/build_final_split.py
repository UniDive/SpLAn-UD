"""
SCRIPT DESCRIPTION:
This script reorganizes CoNLL-U formatted linguistic data based on a JSON split 
configuration file. It reads sentence and document data from individual .conllu files, 
then combines them into new output files according to the groupings specified in a 
split.json configuration file. This is useful for creating different train/test/dev 
splits or other custom corpus divisions.

TODO:
 - add safety checks for unknown document_id or sent_id
 - add error in case of missing/ducplicate sentences in the new corpora (check that the two "set of sent_ids" before/after split is identical)
"""

import sys
import json
import glob
import os
from conllup.conllup import readConlluFile, writeConlluFile


def run_split(base_folder):
	"""
	Main function that orchestrates the corpus splitting process.
	
	Args:
		base_folder (str): Path to the base folder containing an 'original_split' 
						  subdirectory with .conlu files and a split.json config file.
	"""
	
	# Define the path to the folder containing original CoNLL-U files and split configuration
	original_split_folder = os.path.join(base_folder, "original_split")

	# Load the split configuration JSON file that defines how to group documents/sentences
	with open(os.path.join(original_split_folder, "split.json")) as f:
		json_split = json.load(f)

	# Initialize lists to store IDs of documents and sentences that need to be included
	needed_document_ids = []
	needed_sent_ids = []
	
	# Parse the split.json to extract all document IDs and sentence IDs referenced
	for (_, section_list) in json_split.items():
		for section in section_list:
			if "document_ids" in section:
				needed_document_ids += section["document_ids"]
			if "sent_ids" in section:
				needed_sent_ids += section["sent_ids"]

	# Initialize dictionaries to cache loaded documents and sentences
	document_dict = dict()
	sent_dict = dict()

	# Get a list of all .conllu files in the original_split folder
	document_path_list = glob.glob(rf"{original_split_folder}/*.conllu")

	# Load CoNLL-U data from all files and organize by document or sentence ID
	for document_path in document_path_list:
		# Read the CoNLL-U file
		document = readConlluFile(document_path)
		
		# Remove unnecessary metadata column information
		del document[0]['metaJson']['global.columns']
		
		# Extract the document ID from the filename (without extension)
		(document_id, _) = os.path.splitext(os.path.basename(document_path))
		
		# If this document is needed as a whole, store it in the document dictionary
		if document_id in needed_document_ids:
			document_dict[document_id] = document
		else:
			# Otherwise, extract individual sentences and store them by sentence ID
			for sentence in document:
				sent_id = sentence['metaJson']['sent_id']
				sent_dict[sent_id] = sentence

	# Build output files according to the split configuration
	for (output_file, section_list) in json_split.items():
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


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 build_final_split.py base_folder")
	else:
		run_split(sys.argv[1])
