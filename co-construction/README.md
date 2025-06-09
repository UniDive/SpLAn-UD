# How to encode co-construction is dependency treebanks?

Several proposals to encode co-construction are available.

Two alternatives are (see [SpLAn-UD workshop agenda](https://docs.google.com/document/d/1rQ8cMTbSBWlfL2mm5IO2pB4rtbEZk74QRx8Bk8NcvQ8/edit?tab=t.0#heading=h.n6vqecr51w5v)):

 - **Speaker-based**: Each speaker utterance is a new tree, including back-channelling, other single-word utterances. Speaker ID attribute applies to the tree (implicitly all tokens within the tree).
 - **Dependency-based**: A tree may be the outcome of multiple speaker concatenations, each token has a Speaker ID attribute of its own, as there may be arbitrarily many speakers contributing.

---

## "Rhapsodie" encoding

The current version (2.16) of the [SUD_French-Rhapsodie](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie) treebank uses a Speaker-based encoding following the convention:

 - a MISC feature `AttachTo` is on the root node of the sentence implied in a co-construction. The associated value encodes the `sent_id` of the sentence to which it should be attached and the `ID` of the token where the attachement should be done. See [examples](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@2.16&request=pattern%20{%20X%20[AttachTo]%20}) in the corpus.
 - a second feature `Rel` on the same node, encode the dependency relation label (See [`Rel` values used in this encoding](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@2.16&request=pattern%20{%20X%20[AttachTo]%20}&clust1_key=X.__MISC__Rel)) [**NOTE**: the feature `Rel` is named `__MISC__Rel` in Grew syntax because the `Rel` feature is also used as a `FEATS` features in [several UD treebanks](https://tables.grew.fr/?data=ud_feats/FEATS&cols=^Rel$). See [Grew doc](https://grew.fr/doc/conllu/#how-the-misc-field-is-handled-by-grew) for more details].

### Example
An example is given in the file `test/sp_test.conllu` where two sentences from `fr_rhapsodie.sud.train.conllu` (version 2.16) are given:

```
# macrosyntax = ^mais ça continue de $- circuler { avec ESPERLUETTE //
# sent_id = Rhap_D2003-128bis
# speaker = L2
# text = mais ça continue de circuler avec…
1	mais	mais	CCONJ	_	_	3	cc	_	_
2	ça	ça	PRON	_	Gender=Masc|Number=Sing|Person=3|PronType=Dem	3	subj	_	_
3	continue	continuer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
4	de	de	ADP	_	_	3	comp:obl	_	_
5	circuler	circuler	VERB	_	VerbForm=Inf	4	comp:obj	_	Overlap=Rhap_D2003-128ter|Subject=NoRaising
6	avec	avec	ADP	_	_	5	mod	_	Overlap=Rhap_D2003-128ter|SpaceAfter=No
7	…	…	PUNCT	_	_	3	punct	_	Overlap=Rhap_D2003-128ter

# macrosyntax = $L3 "et oui" Messi | -$ >+ maintenant
# sent_id = Rhap_D2003-128ter
# speaker = L3
# text = et oui, Messi maintenant.
1	et	et	CCONJ	_	_	4	cc	_	Overlap=Rhap_D2003-128bis
2	oui	oui	INTJ	_	_	4	discourse	_	Overlap=Rhap_D2003-128bis|SpaceAfter=No
3	,	,	PUNCT	_	_	2	punct	_	Overlap=Rhap_D2003-128bis
4	Messi	Messi	PROPN	_	_	0	root	_	AttachTo=4@Rhap_D2003-128bis|Gender[lex]=Unknown|Overlap=Rhap_D2003-128bis|Rel=comp:obj
5	maintenant	maintenant	ADV	_	_	4	mod	_	SpaceAfter=No
6	.	.	PUNCT	_	_	4	punct	_	_

```
![speaker_based sentence 1](./test/sb_test_1.svg)
![speaker_based sentence 2](./test/sb_test_2.svg)

### Consistency of the encoding
In order to be converted, the speaker-based encoding is supposed to pass some consistency checks. The version 2.16 of SUD_French-Rhapsodie does not follow some if these checks. A branch [`AttachTo`](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie/tree/AttachTo) contains a version which fixes these inconsistencies.

 - The value of the feature `AttachTo` must be of the form `[token_id]@[sent_id]` with a valid reference: `send_id` exists in the treebanks and `token_id` exists in this sentence. See [some ill-formed `AttachTo`](	https://universal.grew.fr/?custom=6846b72e035e6)
 - The feature `AttachTo` must be on the root node. See [exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@2.16&request=pattern%20{%20X%20[AttachTo]%20}%20without%20{%20*%20-[1=root]->%20X%20})
 - The feature `Rel` should be used with the feature `AttachTo` ([no exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@2.16&request=pattern%20{%20X%20[!AttachTo,%20__MISC__Rel]%20}))
 - The feature `AttachTo` should be used with the feature `Rel`. See [exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@2.16&request=pattern%20{%20X%20[AttachTo,%20!__MISC__Rel]%20})


---

## Code
In this folder, a script `sb_to_db.py` is available to convert the Speaker-based encoding used in **SUD_Rhapsodie** to the Dependency-based encoding.
The new relation between in the merged sentences is marked with the suffix `/attach` in the resulting annotation.

The command below builds a dependency-based view of the sentences of the example give above:

```bash
python3 sb_to_db.py test/sp_test.conllu test/db_test.conllu
```

It produces the merged sentence:

![merged_sentence](./test/db_test.svg)

**NOTE:** The `grewpy` library is needed to run this code.
Installation instructions are available [here](https://grew.fr/usage/python/).

## Building Rhapsodie_db

From the data in branch [AttachTo](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie/tree/AttachTo), a dependency-based version of Rhapsodie can be build.

The resulting treebank is available in [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db).

An example of request for cross-speaker dependencies (`/attach` relations): [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=e.label)

## TODO
 - Move `speaker_id` at the token level. In the current version, `speaker_id` metadata are concatenated at the sentence level ([Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=global.speaker)).
 - Two inconsistent `AttachTo` annotations to fix in **SUD_French-Rhapsodie** (temporaly annotated as `SKIP_AttachTo`/`Skip_Rel` to escape the conversion process): [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20X%20[SKIP_AttachTo]%20}).