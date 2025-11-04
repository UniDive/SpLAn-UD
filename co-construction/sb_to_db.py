import os, sys
from termcolor import colored, cprint

from grewpy import set_config, CorpusDraft, Corpus, Request, Graph, GRS
from grewpy.graph import FsEdge

def short_concat (s1,s2):
	"""
	Naive metadata values merging:
	If both have the same value, keep it (sound_url, speaker)
	Else, concatenation with a separator "__" 
	"""
	if s1 == s2:
		return s1
	else:
		return f'{s1}__{s2}'

def merge_dictionaries_with_concat(metadata_1, metadata_2):
	"""
	Merging of the metadata of two sentences.
	"""
	merged_metadata = metadata_1.copy()
	for key, value in metadata_2.items():
		if key in merged_metadata:
			if key == "##MWT_MISC##": # Special encoding in Grew of features on MWT
				merged_metadata[key] = f'{merged_metadata[key]}||{value}'
			else:
				merged_metadata[key] = short_concat(merged_metadata[key], value)
		else:
			merged_metadata[key] = value
	return merged_metadata

def is_anchor(node):
	""" Test if a node is an "anchor" """
	return (node.get("form","") == "__0__")

def merge_list_graph(graphs):
	"""
	Merge a list of graphs in one graph by concatenation of token
	In the merged graph, the nodes_id are line 12#3 for the token number 12 of graph with index 3
	NOTE: The anchor node of the first graph is kept, the anchor node of next graphs are discarded
	NOTE: The new graph is disconnected: all old roots of merged graphs (except the first) have no governor
	"""
	new_graph = Graph()
	for index, graph in enumerate(graphs):
		new_graph.features = new_graph.features | {f'{k}#{index}': graph[k] for k in graph if index == 0 or not is_anchor(graph[k])}
		new_graph.sucs = new_graph.sucs | {f'{k}#{index}': [(f'{tar}#{index}', label) for (tar, label) in graph.sucs[k]] for k in graph.sucs if index == 0 or not is_anchor(graph[k])}
		new_graph.order = new_graph.order + [f'{k}#{index}' for k in graph.order if index == 0 or not is_anchor(graph[k])]
		new_graph.meta = merge_dictionaries_with_concat(new_graph.meta, graph.meta)
	return new_graph

def merge_classes_by_element(partition, sent_id_1, sent_id_2):
	"""
	A partition is encoded as a list of list
	[merge_classes_by_element] is the atomic operation of merging 
	of two classes containing two given elements [sent_id_1] and [sent_id_2]
	NOTE: No value is returned, the given partition is updated.
	"""
	class1_index = None
	class2_index = None
	for i, cls in enumerate(partition):
		if sent_id_1 in cls:
			class1_index = i
		if sent_id_2 in cls:
			class2_index = i
		# If both classes are found, break early
		if class1_index is not None and class2_index is not None:
			break

	if class1_index is None:
		raise (ValueError (f"Unknown sent_id: {sent_id_1}"))
	if class2_index is None:
		raise (ValueError (f"Unknown sent_id: {sent_id_2}"))

	# If both classes are found
	if class1_index != class2_index: # Check if they are different classes
		# keep the order
		smallest = min(class1_index, class2_index)
		largest = max(class1_index, class2_index)
		partition[smallest].extend(partition[largest])
		del partition[largest]

def check_input_data(corpus):
	"""
	Check if the corpus is consistently annotated in AttachTo/Rel
	"""
	validation_requests = [
		'pattern { X [Backchannel]|[Coconstruct] } without { * -[root]-> X }',
	]

	for string_request in validation_requests:
		request = Request(string_request)
		occs = corpus.search(request)
		valid = True
		if len(occs) > 0:
			if valid:
				cprint ('Cannot process data, there are inconsistent annotations:', 'red')
			valid = False
			cprint (f'{len(occs)} times the unexpected request ---> {string_request}', 'red')
			for occ in occs:
				cprint (f'  - {occ["sent_id"]}', 'red')
		if not valid:
			exit (1)

def meta_to_tokens(graph, feature):
	"""
	returns a new graph where the value of the metadata [feature] is copied to each non anchor node of the given [graph]
	"""
	if feature in graph.meta:
		feature_value = graph.meta[feature]
	else:
		cprint (f'no metadata {feature} in {graph.meta["sent_id"]}', 'magenta')
		feature_value = "unknown"

	for node in graph:
		if node != "0":
			graph[node][feature] = feature_value
	return graph

def parse_value (token, deprel="discourse:backchannel"):
	"""
	Split a Backchannel or Coconstruct string: split on "::" if any and then on the last "-"
	Exemple: "BOA3017_91-2" --> ("discourse:backchannel", "BOA3017_91", "2")
	Exemple: "obl::BOA3017_120_121_123_125-21" --> ("obl", "BOA3017_120_121_123_125", "212")
	"""
	rel_ref = token.split("::")
	if len(rel_ref) == 1:
		rel = deprel
		token = token
	elif len(rel_ref) == 2:
		rel = rel_ref[0]
		token = rel_ref[1]
	else:
		raise ValueError (f'Illegal value {token} (more than one "::")')
	index = token.rfind("-")
	if token == -1:
		raise ValueError (f'Illegal value {token} (no hyphen)')
	else:
		return (rel, token[:index], token[index+1:])


def build_merged_corpus (corpus):
	"""
	Main function that turns an input [corpus] into a new corpus with the same data 
	but with "Coconstruct/Backchannel" merged in one graph.
	"""
	occs_coconstruct = corpus.search (Request("pattern { X [Coconstruct]}"), clustering_keys=["X.Coconstruct"])
	occs_backchannel = corpus.search (Request("pattern { X [Backchannel]}"), clustering_keys=["X.Backchannel"])
	occs_all = occs_coconstruct | occs_backchannel

	# Compute the partition (list of list of sent_id) of sentences that should be "merged".
	# All sentences that should be merged are in the same equivalence class.
	partition = [[s] for s in list (corpus)] # Initial partition
	for (key, occs) in occs_all.items():
		(_, tar_sent_id, _) = parse_value(key)
		for src_sent in occs:
			merge_classes_by_element(partition, src_sent["sent_id"], tar_sent_id)

	# Build the new corpus with fake "ATTACH" links
	attach_corpus = CorpusDraft()
	for eq_class in partition:
		if len (eq_class) == 1:
			single_sent_id = eq_class[0]
			single_graph = corpus[single_sent_id]
			attach_corpus[single_sent_id] = single_graph
		else:
			graphs = [meta_to_tokens (corpus[sent_id], "speaker_id") for sent_id in eq_class]
			merged_graph = merge_list_graph (graphs)

			# Add cross sentence edges
			for (key, occs) in occs_all.items():
				(rel, tar_sent_id, tar_token) = parse_value(key)
				if tar_sent_id in eq_class:
					tar_index = eq_class.index(tar_sent_id)
					for occ in occs:
						src_sent_id = occ["sent_id"]
						src_index = eq_class.index(src_sent_id)
						src_token = occ["matching"]["nodes"]["X"]
						full_src_token = f'{src_token}#{src_index}'
						full_tar_token = f'{tar_token}#{tar_index}'
						if full_tar_token not in merged_graph:
							raise (ValueError (f"Unknown token_id: {tar_token} in sent_id: {tar_sent_id}" ))
						old = merged_graph.sucs.get(full_tar_token, [])
						merged_graph.sucs[full_tar_token] = old + [(full_src_token, FsEdge({'1': rel, 'type': 'attach'}))]

			attach_corpus[merged_graph.meta["sent_id"]] = merged_graph

	# A GRS is used to move the deprel annotation from the feature Rel to the edge.
	grs = GRS("attach.grs")
	final_corpus = grs.apply(Corpus(attach_corpus))
	return (final_corpus)

if __name__ == "__main__":
	try:
		set_config ("ud")
		if len (sys.argv) < 3:
			raise (ValueError ("Two arguments needed"))
		input_corpus = Corpus (sys.argv[1])
		# check_input_data(input_corpus)
		output_corpus = build_merged_corpus (input_corpus)
		with open(sys.argv[2], 'w') as f:
			f.write (output_corpus.to_conll())
		cprint (f"Merged from {len(input_corpus)} sentences to {len(output_corpus)}", "green")
	except ValueError as msg:
		cprint(f'Cannot process: {msg}', 'red')
		exit (1)

