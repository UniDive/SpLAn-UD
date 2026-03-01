import sys
import argparse
import json
from pathlib import Path
from conllup.conllup import readConlluFile, writeConlluFile
from termcolor import colored, cprint

METADATA_DEPENDENCIES = {
	"document_id": "sound_url",
	"speaker_id": "speaker_sex",
}

def share_conllu(shared_metadata, document_id, conllu):
	"""Extract and deduplicate metadata from a sentence."""
	meta = conllu['metaJson']
	meta["document_id"] = document_id
	keys_to_delete = ["document_id"]

	for main_key, sub_key in METADATA_DEPENDENCIES.items():
		if main_key not in meta:
			continue

		main_value = meta[main_key]
		sub_value = meta.get(sub_key)

		if sub_value is None:
			raise KeyError(f"Missing '{sub_key}' when '{main_key}' is present")

		# Navigate nested dictionary
		sub_dict = shared_metadata.setdefault(main_key, {})
		subsub_dict = sub_dict.setdefault(main_value, {})

		# Check for conflicts
		if sub_key in subsub_dict and subsub_dict[sub_key] != sub_value:
			raise ValueError(
				f"Conflicting values for {main_key}={main_value}, {sub_key}: "
				f"{subsub_dict[sub_key]} vs {sub_value}"
			)

		subsub_dict[sub_key] = sub_value
		keys_to_delete.append(sub_key)

	# Remove deduplicated keys from individual files
	for key in keys_to_delete:
		meta.pop(key, None)

def share(in_folder, out_folder):
	"""Process all .conllu files and extract shared metadata."""
	in_path = Path(in_folder)
	out_path = Path(out_folder)

	if not in_path.is_dir():
		cprint(f"Error: '{in_folder}' is not a valid directory", "red")
		sys.exit(1)

	out_path.mkdir(parents=True, exist_ok=True)
	shared_metadata = {}

	document_files = sorted(in_path.glob("*.conllu"))

	for document_file in document_files:
		document_id = document_file.stem
		out_file = out_path / document_file.name

		try:
			conllu = readConlluFile(document_file)
			for sentence in conllu:
				share_conllu(shared_metadata, document_id, sentence)
			writeConlluFile(out_file, conllu, overwrite=True)
		except KeyError as e:
			cprint(f"Error: Missing metadata in {document_file.name}: {e}", "red")
		except ValueError as e:
			cprint(f"Error: Invalid metadata in {document_file.name}: {e}", "red")
		except Exception as e:
			cprint(f"Unexpected error processing {document_file.name}: {type(e).__name__}: {e}", "red")

	metadata_file = Path(out_folder) / "metadata.json"
	with open(metadata_file, "w") as fp:
		json.dump(shared_metadata, fp, indent=2, ensure_ascii=False)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='''Process .conllu files in `in_folder` and "share" metadata.
Files produced in the `out_folder`:
 - new .conllu files without the shared metadata
 - a file `metadata.json` recording the found shared metadata
WARNING: existing files in `out_folder` will be overwritten''',
    formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument(
		"in_folder",
		help="Path to the folder containing input .conllu files"
	)
	parser.add_argument(
		"out_folder",
		help="Path to the folder for storing unshared .conllu files"
	)

	args = parser.parse_args()

	share(args.in_folder, args.out_folder)

	if len(sys.argv) != 3:
		cprint("Usage: python script.py <in_folder> <out_folder>", "red")
		sys.exit(1)

	in_folder, out_folder = sys.argv[1], sys.argv[2]
	share(in_folder, out_folder)
