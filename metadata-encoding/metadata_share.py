import sys
import os
import json
from conllup.conllup import readConlluFile, writeConlluFile

metadata_dependencies = {
	# main_key: sub_key
	"document_id": "sound_url",
	"speaker_id": "speaker_sex",
}


def share_conllu(shared_metadata, document_id, conllu):

	conllu['metaJson']["document_id"] = document_id
	keys_to_delete = ["document_id"]
	for key, value in conllu['metaJson'].items():
		if key in metadata_dependencies:
			main_key = key
			sub_key = metadata_dependencies[key]
			main_value = conllu['metaJson'][main_key] # TODO: handle Keyerror
			sub_value = conllu['metaJson'][sub_key] # TODO: handle Keyerror

			sub_dict = shared_metadata.get(main_key,dict())
			subsub_dict = sub_dict.get(main_value, dict())
			if sub_key in subsub_dict:
				if subsub_dict[sub_key] != sub_value:
					raise (ValueError ("Ambiguous"))
			subsub_dict[sub_key] = sub_value
			sub_dict[main_value] = subsub_dict
			shared_metadata[main_key] = sub_dict
			keys_to_delete.append(sub_key)
	for key in keys_to_delete:
		del conllu['metaJson'][key]

def share(in_folder, out_folder):
	shared_metadata = dict()

	if not os.path.isdir(in_folder):
		print(f"Arg 1 ({in_folder}) is not a folder")
		sys.exit(1)

	os.makedirs(out_folder, exist_ok=True)

	# Process .conllu files
	document_files = [f for f in os.listdir(in_folder) if f.endswith(".conllu")]

	for document_file in document_files:
		document_id = os.path.splitext(document_file)[0]
		out_file = os.path.join(out_folder, document_file)

		try:
			conllu = readConlluFile(os.path.join(in_folder, document_file))
			for sentence in conllu:
				share_conllu(shared_metadata, document_id, sentence)
			writeConlluFile(out_file, conllu, overwrite=True)
		except Exception as e:
			print(f"Error processing {document_file}: {e}")
	return (shared_metadata)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Expect two args: in_folder, out_folder")
		sys.exit(1)

	in_folder, out_folder = sys.argv[1], sys.argv[2]
	shared_metadata = share(in_folder, out_folder)

	with open(os.path.join(out_folder,"metadata.json"), "w") as fp:
		json.dump(shared_metadata, fp, indent=2)