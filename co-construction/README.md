# How to encode co-construction is dependency treebanks?

Two alternatives are (see [SpLAn-UD working document](https://docs.google.com/document/d/1EwAirGG7U3riZPsT04TzIOoQJ60atj3mUi-TnEKL0oE)):

 - **Speaker-based**: Each speaker utterance is a new tree, including back-channelling, other single-word utterances. Speaker ID attribute applies to the tree (implicitly all tokens within the tree).
 - **Dependency-based**: A tree may be the outcome of multiple speaker concatenations, each token has a Speaker ID attribute of its own, as there may be arbitrarily many speakers contributing.

---

# Examples

## Basic examples given in the UniDive document

### Speaker-based
![speaker-based sentence 1](./test/guidelines/speaker_based_1.svg)
![speaker-based sentence 2](./test/guidelines/speaker_based_2.svg)
![speaker-based sentence 3](./test/guidelines/speaker_based_3.svg)

### Dependency-based
![dependency-based sentence](./test/guidelines/dependency_based.svg)

---

## Examples from SUD_French-Rhapsodies

![speaker-based sentence 1](./test/Rhapsodie/sb_test_1.svg)
![speaker-based sentence 2](./test/Rhapsodie/sb_test_2.svg)

![dependency-based sentence](./test/Rhapsodie/db_test.svg)

More examples can be seen in [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db):
 - request for cross-speaker dependencies (`/attach` relations): [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=e.label)
 - `speaker_id` metadata is concatenated at the sentence level: [Grew-match](https://universal.grew.fr/?corpus=SUD_French-Rhapsodie_db&request=pattern%20{%20e:%20X%20-[type=attach]->%20Y%20}&clust1_key=meta.speaker)

---

## Code
A script called `sb_to_db.py` is available in this folder to convert the Speaker-based encoding to the Dependency-based encoding.
In the merged sentences, the new relations are marked with the suffix `/attach`.

The command below builds a dependency-based view of the sentences of the example give above:

```bash
python3 sb_to_db.py test/guidelines/speaker_based.conllu test/guidelines/dependency_based.conllu
```

**NOTE:** The `grewpy` library is required to run this code.
Installation instructions are available [here](https://grew.fr/usage/python/).
