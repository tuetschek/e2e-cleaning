

Cleaning the E2E NLG Dataset
============================


1.) Re-annotate MRs in the data:
```
./slot_error.py -f train-fixed.csv path/to/trainset.csv
./slot_error.py -f devel-fixed.csv path/to/devset.csv
./slot_error.py -f test-fixed.csv path/to/testset_w_refs.csv
```


2.) Remove instances with overlapping MRs (after reannotation). Keeps the test set intact; if an instance overlaps between train and dev set, it's removed from the train set:

```
./remove_overlaps.py train-fixed.csv devel-fixed.csv test-fixed.csv
```

