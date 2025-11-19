import sys
import os
import json
from conllup.conllup import readConlluFile, writeConlluFile

def expand(shared_meta, sample_id, conllu):
	# Update conllu['metaJson'] with sample-specific metadata
	sample_keys = shared_meta.get('sample_id', {}).get(sample_id, {})
	conllu['metaJson'].update(sample_keys)

	# Prepare to expand conllu['metaJson'] with additional metadata from shared_meta
	additional_keys = {}
	for key, value in conllu['metaJson'].items():
		if key in shared_meta and value in shared_meta[key]:
			additional_keys.update(shared_meta[key][value])

	# Update conllu['metaJson'] with the collected additional keys
	conllu['metaJson'].update(additional_keys)

def unshare(in_folder, out_folder):
	if not os.path.isdir(in_folder):
		print(f"Arg 1 ({in_folder}) is not a folder")
		sys.exit(1)

	os.makedirs(out_folder, exist_ok=True)

	# Load shared metadata
	try:
		with open(os.path.join(in_folder, "metadata.json")) as meta_file:
			shared_meta = json.load(meta_file)
	except FileNotFoundError:
		print(f"metadata.json not found in {in_folder}")
		sys.exit(1)
	except json.JSONDecodeError:
		print("Error decoding JSON from metadata.json")
		sys.exit(1)

	# Process .conllu files
	conllu_files = [f for f in os.listdir(in_folder) if f.endswith(".conllu")]
	for sample in conllu_files:
		sample_id = os.path.splitext(sample)[0]
		out_file = os.path.join(out_folder, sample)

		try:
			conllu = readConlluFile(os.path.join(in_folder, sample))
			for sentence in conllu:
				expand(shared_meta, sample_id, sentence)
			writeConlluFile(out_file, conllu, overwrite=True)
		except Exception as e:
			print(f"Error processing {sample}: {e}")

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Expect two args: in_folder, out_folder")
		sys.exit(1)

	in_folder, out_folder = sys.argv[1], sys.argv[2]

	unshare(in_folder, out_folder)
