
Cleaning Semantic Noise in the E2E dataset
==========================================

An update release of [E2E NLG Challenge data](http://www.macs.hw.ac.uk/InteractionLab/E2E/) with cleaned MRs and scripts, 
accompanying the following paper:

Ondřej Dušek, David M. Howcroft, and Verena Rieser (2019): [Semantic Noise Matters for Neural Natural Language Generation](https://www.aclweb.org/anthology/W19-8652/). In _INLG_, Tokyo, Japan.


Cleaned data
------------

The fully cleaned E2E NLG Challenge data can be found in [cleaned-data](cleaned-data/). 
The training and development set are filtered so that they don't overlap the test set, hence the `no-ol` naming.

The partially cleaned data (see paper) are under [partially-cleaned-data](partially-cleaned-data/).
Do not use these unless you have a good reason to do so.


### Cleaning process ###

This is just documenting what we have done to get the cleaned data; you do not need to run this.


1.) Re-annotate MRs in the data (use `-t` if you want a partial fix only):
```
./slot_error.py -f train-fixed.csv path/to/trainset.csv
./slot_error.py -f devel-fixed.csv path/to/devset.csv
./slot_error.py -f test-fixed.csv path/to/testset_w_refs.csv
```

2.) Remove instances with overlapping MRs (after reannotation). Keeps the test set intact; if an instance overlaps between train and dev set, it's removed from the train set:

```
./remove_overlaps.py train-fixed.csv devel-fixed.csv test-fixed.csv
```


Experiments with TGen
---------------------

We used the data with default [TGen](https://github.com/UFAL-DSG/tgen) settings 
for the [E2E Challenge](https://github.com/UFAL-DSG/tgen/tree/master/e2e-challenge),
with validation on the development set (additional training parameter `-v input/devel-das.txt,input/devel-text.txt`) 
and evaluation on the test set (both original and cleaned).

To get the plain seq2seq configuration ("TGen-"), we set the `classif_filter` parameter in the 
`config/config.yaml` file to `null`.
To use the slot error script as reranker ("TGen+"), we set `classif_filter` in the following way:

```
    classif_filter: {'model': 'e2e_patterns'}
```

Note that a version of the `slot_error.py` script is 
[included in TGen code](https://github.com/UFAL-DSG/tgen/blob/master/tgen/e2e/slot_error.py) 
for simpler usage.


System outputs
--------------

You can find system outputs of all versions of TGen trained and tested on original and cleaned data under [system-outputs](system-outputs/). These system outputs were used to obtain the top halves of Table 2 & 3 in the INLG paper.

There are 4 different systems included:
* _SC-LSTM_ (Wen et al., 2015)
* _TGen-minus_ – TGen without any reranker
* _TGen-std_ – TGen with the standard LSTM reranker trained on the same training data
* _TGen-plus_ – TGen with the rule-based pattern matching reranker used to clean the data (“oracle”)
All systems were run 5 times with different random network initialization (run0-run4).
