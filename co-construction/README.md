# How to encode co-construction is dependency treebanks?

There are several proposals available for encoding co-construction.

Two alternatives are (see [SpLAn-UD workshop agenda](https://docs.google.com/document/d/1rQ8cMTbSBWlfL2mm5IO2pB4rtbEZk74QRx8Bk8NcvQ8/edit?tab=t.0#heading=h.n6vqecr51w5v)):

 - **Speaker-based**: Each speaker utterance is a new tree, including back-channelling, other single-word utterances. Speaker ID attribute applies to the tree (implicitly all tokens within the tree).
 - **Dependency-based**: A tree may be the outcome of multiple speaker concatenations, each token has a Speaker ID attribute of its own, as there may be arbitrarily many speakers contributing.

---

## "Rhapsodie" encoding

The current version (`master` branch) of the [SUD_French-Rhapsodie](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie) treebank uses a Speaker-based encoding following the convention:

 - A `MISC` feature, `AttachTo`, is on the root node of a sentence that is implied in a co-construction.
 The associated value encodes the `sent_id` of the sentence to which it should be attached, as well as the `ID` of the token to which it should be attached.
 See the [examples](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@latest&request=pattern%20{%20X%20[AttachTo]%20}) in the corpus.
 - A second feature `Rel` on the same node, encodes the dependency relation label.
 See [`Rel` values used in this encoding](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@latest&request=pattern%20{%20X%20[AttachTo]%20}&clust1_key=X.__MISC__Rel)) (**NOTE**: The feature `Rel` is named `__MISC__Rel` in Grew syntax because the `Rel` feature is also used as a feature in `FEATS` by [several UD treebanks](https://tables.grew.fr/?data=ud_feats/FEATS&cols=^Rel$).
 See [Grew documentation](https://grew.fr/doc/conllu/#how-the-misc-field-is-handled-by-grew) for more details).

### Example
An example is given in the file `test/sp_test.conllu` where two sentences from `fr_rhapsodie.sud.train.conllu` (version 2.16) are given:

```
# sent_id = Rhap_D2003-151
# speaker = L2
# speaker_id = §LM16
# text = mais ça continue de circuler avec…
1	mais	mais	CCONJ	_	_	3	cc	_	_
2	ça	ça	PRON	_	Gender=Masc|Number=Sing|Person=3|PronType=Dem	3	subj	_	_
3	continue	continuer	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
4	de	de	ADP	_	_	3	comp:obl	_	_
5	circuler	circuler	VERB	_	VerbForm=Inf	4	comp:obj	_	Overlap=Rhap_D2003-152|Subject=NoRaising
6	avec	avec	ADP	_	_	5	mod	_	Overlap=Rhap_D2003-152|SpaceAfter=No
7	…	…	PUNCT	_	_	3	punct	_	Overlap=Rhap_D2003-128ter

# sent_id = Rhap_D2003-152
# speaker = L3
# speaker_id = §LM17
# text = et oui, Messi maintenant.
1	et	et	CCONJ	_	_	4	cc	_	Overlap=Rhap_D2003-151
2	oui	oui	INTJ	_	_	4	discourse	_	Overlap=Rhap_D2003-151|SpaceAfter=No
3	,	,	PUNCT	_	_	2	punct	_	Overlap=Rhap_D2003-128bis
4	Messi	Messi	PROPN	_	_	0	root	_	AttachTo=6@Rhap_D2003-151|Gender[lex]=Unknown|Overlap=Rhap_D2003-151|Rel=comp:obj
5	maintenant	maintenant	ADV	_	_	4	mod	_	SpaceAfter=No
6	.	.	PUNCT	_	_	4	punct	_	_

```
![speaker_based sentence 1](./test/sb_test_1.svg)
![speaker_based sentence 2](./test/sb_test_2.svg)

### Consistency of the encoding
In order to be converted, the speaker-based encoding must pass certain consistency checks.
Version 2.16 of **SUD_French-Rhapsodie** does not adhere to all of these checks.
The branch called [`master`](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie/tree/master) contains a version that fixes these inconsistencies.

 - The feature `AttachTo` must be on the root node. See [exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@latest&request=pattern%20{%20X%20[AttachTo]%20}%20without%20{%20*%20-[1=root]->%20X%20})
 - The feature `Rel` should be used with the feature `AttachTo` ([no exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@latest&request=pattern%20{%20X%20[!AttachTo,%20__MISC__Rel]%20}))
 - The feature `AttachTo` should be used with the feature `Rel`. See [exceptions](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie@latest&request=pattern%20{%20X%20[AttachTo,%20!__MISC__Rel]%20})


---

## Code
A script called `sb_to_db.py` is available in this folder to convert the Speaker-based encoding used in **SUD_French-Rhapsodie** to the Dependency-based encoding.
In the merged sentences, the new relations are marked with the suffix `/attach` in the resulting annotation.

The command below builds a dependency-based view of the sentences of the example give above:

```bash
python3 sb_to_db.py test/sp_test.conllu test/db_test.conllu
```

It produces the merged sentence:

![merged_sentence](./test/db_test.svg)

**NOTE:** The `grewpy` library is required to run this code.
Installation instructions are available [here](https://grew.fr/usage/python/).

## Building Rhapsodie_db

A dependency-based version of Rhapsodie can be built from the data in the [master](https://github.com/surfacesyntacticud/SUD_French-Rhapsodie/tree/master) branch.

The resulting treebank is available in [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db).

An example of request for cross-speaker dependencies (`/attach` relations): [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=e.label)

In the current version, `speaker_id` metadata is concatenated at the sentence level ([Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=meta.speaker)).
