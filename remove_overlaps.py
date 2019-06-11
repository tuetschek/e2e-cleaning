#!/usr/bin/env python3

import re
from argparse import ArgumentParser

import pandas as pd

from tgen.data import DA


def parse_mr(mr_text):
    return DA.parse_diligent_da(mr_text).get_delexicalized(set(['name', 'near']))

def main(args):

    train = pd.read_csv(args.input_train, encoding="UTF-8")
    devel = pd.read_csv(args.input_devel, encoding="UTF-8")
    test = pd.read_csv(args.input_test, encoding="UTF-8")

    test_orig_mrs = set([parse_mr(mr) for mr in list(test['orig_mr'])])
    test_mrs = set([parse_mr(mr) for mr in list(test['mr'])])

    print("Checking devel set...")

    # check devel data:
    dev_idx_to_del = []
    dev_mrs = set()
    for idx, inst in devel.iterrows():
        mr = parse_mr(inst.mr)
        dev_mrs.add(mr)
        if mr in (test_mrs | test_orig_mrs):
            dev_idx_to_del.append(idx)

    print("To delete: %d / %d instances from devel, %d / %d distinct MRs" %
          (len(dev_idx_to_del), len(devel), len(dev_mrs & (test_mrs | test_orig_mrs)), len(dev_mrs)))
    devel = devel.drop(dev_idx_to_del)

    output_devel = re.sub('(\.[^.]+)$', args.suffix + r'\1', args.input_devel)
    print("Writing fixed %s..." % output_devel)
    devel.to_csv(output_devel, encoding='UTF-8', index=False)

    print("Checking train set...")

    # check train data
    train_idx_to_del = []
    train_mrs = set()
    for idx, inst in train.iterrows():
        mr = parse_mr(inst.mr)
        train_mrs.add(mr)
        if mr in (dev_mrs | test_mrs | test_orig_mrs):
            train_idx_to_del.append(idx)

    print("To delete: %d / %d instances from devel, %d / %d distinct MRs" %
          (len(train_idx_to_del), len(train), len(train_mrs & (dev_mrs | test_mrs | test_orig_mrs)), len(train_mrs)))
    train = train.drop(train_idx_to_del)

    output_train = re.sub('(\.[^.]+)$', args.suffix + r'\1', args.input_train)
    print("Writing fixed %s..." % output_train)
    train.to_csv(output_train, encoding='UTF-8', index=False)



if __name__ == '__main__':
    ap = ArgumentParser(description='Remove overlapping MRs from different parts of the dataset (aiming to keep the test set intact)')
    ap.add_argument('--suffix', '-s', type=str, default='.no-ol', help='Suffix to add to output filenames')
    ap.add_argument('input_train', type=str, help='Input training set CSV')
    ap.add_argument('input_devel', type=str, help='Input development set CSV')
    ap.add_argument('input_test', type=str, help='Input test set CSV')
    args = ap.parse_args()

    main(args)

