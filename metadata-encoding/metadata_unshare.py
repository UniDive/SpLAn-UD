import sys
import json
from pathlib import Path
from conllup.conllup import readConlluFile, writeConlluFile

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

def unshare(in_folder, out_folder):
	"""Restore shared metadata to individual .conllu files."""
	in_path = Path(in_folder)
	out_path = Path(out_folder)

	if not in_path.is_dir():
		print(f"Error: '{in_folder}' is not a valid directory")
		sys.exit(1)

	out_path.mkdir(parents=True, exist_ok=True)

	# Load shared metadata
	metadata_file = in_path / "metadata.json"
	try:
		with open(metadata_file, encoding="utf-8") as meta_file:
			shared_meta = json.load(meta_file)
	except FileNotFoundError:
		print(f"Error: metadata.json not found in {in_folder}")
		sys.exit(1)
	except json.JSONDecodeError as e:
		print(f"Error: Invalid JSON in metadata.json: {e}")
		sys.exit(1)

	# Process .conllu files
	conllu_files = sorted(in_path.glob("*.conllu"))

	for conllu_file in conllu_files:
		document_id = conllu_file.stem
		out_file = out_path / conllu_file.name

		try:
			conllu = readConlluFile(conllu_file)
			for sentence in conllu:
				expand(shared_meta, document_id, sentence)
			writeConlluFile(out_file, conllu, overwrite=True)
		except Exception as e:
			print(f"Error processing {conllu_file.name}: {type(e).__name__}: {e}")

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python script.py <in_folder> <out_folder>")
		sys.exit(1)

	in_folder, out_folder = sys.argv[1], sys.argv[2]
	unshare(in_folder, out_folder)
