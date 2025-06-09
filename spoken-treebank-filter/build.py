import pathlib
import conllu
import sys

import filters


if len(sys.argv) < 3:
	print("Please run `python3 script.py [SOURCE_DIR] [DEST_DIR]`")
	sys.exit(1)

source_path = sys.argv[1]
destination_path = sys.argv[2]

spoken_only = [x.strip() for x in open("spoken_only.txt", "r", encoding="utf-8").readlines()]

spoken_subset = [x.strip().split("\t") for x in open("spoken_subset.txt", "r", encoding="utf-8").readlines()]


for treebank in spoken_only:
	print(f"Reading treebank {treebank}...")
	source_dir = f"{source_path}/{treebank}/"
	destination_dir = f"{destination_path}/{treebank}"
	try:
		pathlib.Path(destination_dir).symlink_to(source_dir)
	except FileExistsError as e:
		print("Symlink already in place")


for treebank, meta_tag in spoken_subset:
	print(f"Reading treebank {treebank}...")
	source_dir = f"{source_path}/{treebank}/"
	destination_dir = f"{destination_path}/{treebank}"
	pathlib.Path(destination_dir).mkdir(parents=True, exist_ok=True)

	for filename in pathlib.Path(source_dir).glob("*.conllu"):
		print(f"Reading file {filename}...")
		file_stem = filename.stem
		with open(filename, encoding="utf-8") as fin, \
			open(pathlib.Path(destination_dir).joinpath(f"{file_stem}.selected.conllu"), "w", encoding="utf-8") as fout:

			fun1 = lambda meta: meta_tag in meta
			fun2 = getattr(filters, treebank.replace("-", "_"))
			sentences = conllu.parse_incr(fin)

			condition = False

			for sentence in sentences:
				metadata = sentence.metadata

				if fun1(metadata):
					if fun2(metadata):
						condition = True
						fout.write(sentence.serialize())
					else:
						condition = False
				else:
					if condition:
						fout.write(sentence.serialize())