#!/usr/bin/env python3
# -"- encoding: utf-8 -"-
# the script is Python2/3 compatible

from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentParser
import pandas as pd
import re
import codecs
import json
import sys
from tgen.data import DA

REALIZATIONS = {
    'area': {
        'city centre': [
            '(?:city|town) cent(?:re|er)',
            'cent(?:re|er) of (?:the )?(?:city|town)',
            'in the cent(?:re|er)',
        ],
        'riverside': [
            'riverside',
            '(?:near|by|at|close to|along|on|off|beside) the river',
        ],
    },
    'eat_type': {
        'coffee shop': [
            'coffee[- ]+shop',
            'caf[eé]',
            'coffee',
        ],
        'pub': [
            'pub',
        ],
        'restaurant': [
            'restaurant',
        ],
    },
    'family_friendly': {
        'no': [
            '(?:isn\'t|not|non|no)[ -]+(?:\w+ ){0,2}(?:child|children|family|kids|kid)[ -]+(?:friendly|orien(?:ta)?ted)',
            '(?:child|children|family|kids|kid)[ -]+unfriendly',
            'adults?[ -]+only',
            'only for adults',
            '(?:no|not) (?:kids|children|famil(?:y|ies))',
            '(?:not|no)(?: good| suitable| friendly| orien(?:ta)?ted| open(?:ed))? (?:at|for|to|with)(?: the)? (?:kids|children|family|families|all age)',
            '(?:kids?|child(?:ren)?|famil(?:y|ies)) (?:are|is)(?:n\'t| not) (?:welcome|allowed|accepted)',
            '(?:does not|doesn\'t) (?:welcome|allow|accept) (?:\w+ ){0,2}(?:kids?|child(?:ren)?|famil(?:y|ies)|all age)',
            'adult (?:establishment|venue|place|establish)',
        ],
        'yes': [
            'for (?:kids|children|family|families)',
            'family place',
            'place to bring the(?: whole)? family',
            '(?:friendly|suitable|good|orien(?:ta)?ted|open(?:ed)) (?:at|with|to|for)(?: the)(?:kids?|child(?:ren)?|famil(?:y|ies)?|all age)',
            '(?:child|children|family|kids|kid)[ -]+(?:friendly|orien(?:ta)?ted)',
            '(?:kids?|child(?:ren)?|famil(?:y|ies)) (?:are|is) (?:welcome|allowed|accepted)',
            '(?:welcomes?|allows?|accepts?) (?:\w+ ){0,2}(?:kids?|child(?:ren)?|famil(?:y|ies)|all age)',
        ],
    },
    'food': {
        'Chinese': ['Chinese', 'Chines'],
        'English': ['English', 'British'],
        'Fast food': ['Fast food'],
        'French': ['French'],
        'Indian': ['Indian'],
        'Italian': ['Italian'],
        'Japanese': ['Japanese'],
    },
    'name': [
        'Alimentum',
        'Aromi',
        'Bibimbap House',
        'Blue Spice',
        'Browns Cambridge',
        'Clowns',
        'Cocum',
        'Cotto',
        'Fitzbillies',
        'Giraffe',
        'Green Man',
        'Loch Fyne',
        'Midsummer House',
        'Strada',
        'Taste of Cambridge',
        'The Cambridge Blue',
        'The Cricketers',
        'The Dumpling Tree',
        'The Eagle',
        'The Golden Curry',
        'The Golden Palace',
        'The Mill',
        'The Olive Grove',
        'The Phoenix',
        'The Plough',
        'The Punter',
        'The Rice Boat',
        'The Twenty Two',
        'The Vaults',
        'The Waterman',
        'The Wrestlers',
        'Travellers Rest Beefeater',
        'Wildwood',
        'Zizzi',
    ],
    'near': [
        'All Bar One',
        'Avalon',
        'Burger King',
        'Café Adriatic',
        'Café Brazil',
        'Café Rouge',
        'Café Sicilia',
        'Clare Hall',
        'Crowne Plaza Hotel',
        'Express by Holiday Inn',
        'Rainbow Vegetarian Café',
        'Raja Indian Cuisine',
        'Ranch',
        'The Bakers',
        'The Portland Arms',
        'The Rice Boat',
        'The Six Bells',
        'The Sorrento',
        'Yippee Noodle Bar',
    ],
    'price_range': {
        "cheap": [
            "(?:inexpensive|cheap)(?:ly)?",
            "low[- ]+price[ds]?",
            "affordabl[ey]",
            "prices?(?: range)?(?: \w+){0,3} low",
        ],
        "less than £20": [
            "(?:inexpensive|cheap)(?:ly)?",
            "affordabl[ey]",
            "(?:less than|under) £? *20",
            "moderately priced",
            "low[- ]+price[ds]?",
            "prices?(?: range)?(?: \w+){0,3} low",
        ],
        "more than £30": [
            "(?:more than|over) £? *30",
            "high[- ]+price[ds]?",
            "expensive",
            "not cheap",
            "prices?(?: range)?(?: \w+){0,3} high",
        ],
        "high": [
            "high[- ]+price[ds]?",
            "expensive",
            "prices?(?: range)?(?: \w+){0,3} high",
        ],
        "moderate": [
            "(?:moderate|reasonable|ok|average)(?:ly)?[- ]+price[ds]?",
            "not cheap",
            "affordable",
            "mid[- ]+(?:range[- ]+)price[ds]?",
            "prices?(?: range)?(?: \w+){0,3} (?:ok|average|moderate|reasonable)",
        ],
        "£20-25": [
            "£? *20 *(?:[-–]*|to) *25",
            "(?:moderate|reasonable|ok|average)(?:ly)?[- ]+price[ds]?",
            "prices?(?: range)?(?: \w+){0,3} (?:ok|average|moderate|reasonable)",
            "affordable",
        ]
    },
    'rating': {
        "1 out of 5": [
            "(?:1|one)[- ]+stars?",
            "(?:1|one)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?(?:low|bad|poor)",
            "(?:low|bad|poor)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
        "3 out of 5": [
            "(?:3|three)[- ]+stars?",
            "(?:3|three)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?average",
            "average(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
        "5 out of 5": [
            "(?:5|five)[- ]+stars?",
            "(?:5|five)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?high",
            "(?:high|excellent|very good|great)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
        "high": [
            "(?:5|five)[- ]+stars?",
            "(?:5|five)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?high",
            "(?:high|excellent|very good|great)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
        "average": [
            "(?:3|three)[- ]+stars?",
            "(?:3|three)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?average",
            "average(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
        "low": [
            "(?:1|one)[- ]+stars?",
            "(?:1|one)(?: out)? of (?:5|five)",
            "(?:rat(?:ings?|e[ds]?)|reviews?|standards?|quality)(?: \w+){0,2} (?:as )?(?:low|bad|poor)",
            "(?:low|bad|poor)(?:ly)?(?:[ -]+\w+){0,2}[ -]+(?:rat(?:ings?|ed)|reviews?|standards?|quality)",
        ],
    },
}


def compile_patterns(patterns):
    """Compile a list of patterns into one big option regex. Note that all of them will match whole words only."""
    # pad intent patterns with \b (word boundary), unless they contain '^'/'$' (start/end)
    return re.compile('|'.join([((r'\b' if not pat.startswith('^') else '') + pat +
                                 (r'\b' if not pat.endswith('$') else ''))
                                for pat in patterns]),
                      re.I | re.UNICODE)


# compile realization patterns
for slot in REALIZATIONS.keys():
    if isinstance(REALIZATIONS[slot], list):
        REALIZATIONS[slot] = compile_patterns(REALIZATIONS[slot])
    else:
        for value in REALIZATIONS[slot].keys():
            REALIZATIONS[slot][value] = compile_patterns(REALIZATIONS[slot][value])


class Match(object):
    """Realization pattern match in the system output"""

    def __init__(self, slot, value, regex_match):
        self.slot = slot
        self.value = value
        self._start = regex_match.start()
        self._end = regex_match.end()

    def is_same_string(self, other):
        return (self._start == other._start and self._end == other._end)

    def is_substring(self, other):
        return ((self._start > other._start and self._end <= other._end) or
                (self._start >= other._start and self._end < other._end))

    def __eq__(self, other):
        return (self.slot == other.slot and self.value == other.value and self.is_same_string(other))

    def __str__(self):
        return 'Match[%s=%s:%d-%d]' % (self.slot, self.value, self._start, self._end)

    def __repr__(self):
        return str(self)


def check_output(mr, ref):
    """Check conformity of the given system output (ref) with the input MR."""
    # convert MR to dict for comparing & checking against
    mr_dict = {dai.slot: {dai.value.lower(): 1} for dai in mr.dais}

    # create MR dict representation of the output text
    # first, collect all value matches
    matches = []
    for slot in REALIZATIONS.keys():
        # verbatim slot
        if not isinstance(REALIZATIONS[slot], dict):
            matches.extend([Match(slot, match.group(0).lower(), match)
                            for match in REALIZATIONS[slot].finditer(ref)])
        # slot with variable realizations
        else:
            # collect all matches for all values
            for value in REALIZATIONS[slot].keys():
                matches.extend([Match(slot, value.lower(), match)
                                for match in REALIZATIONS[slot][value].finditer(ref)])

    # then filter out those that are substrings/duplicates (let only one value match,
    # preferrably the one indicated by the true MR -- check with the MR dict)
    filt_matches = []
    for match in matches:
        skip = False
        for other_match in matches:
            if match is other_match:
                continue
            if (match.is_substring(other_match) or
                (match.is_same_string(other_match) and
                 (other_match.value in mr_dict.get(other_match.slot, {}).keys() or other_match in filt_matches))):
                skip = True
                break
        if not skip:
            filt_matches.append(match)

    # now put it all into a dict
    out_dict = {}
    for match in filt_matches:
        out_dict[match.slot] = out_dict.get(match.slot, {})
        out_dict[match.slot][match.value] = out_dict[match.slot].get(value, 0) + 1

    # count the errors in the output, looking at the MR
    added, missing, valerr, repeated = 0, 0, 0, 0
    diff = {}
    for slot in set(mr_dict.keys()) | set(out_dict.keys()):
        if slot in mr_dict and slot not in out_dict:
            missing += sum(mr_dict[slot].values())
            diff[slot] = {val: -count for val, count in mr_dict[slot].items()}
        elif slot not in mr_dict and slot in out_dict:
            added += sum(out_dict[slot].values())
            diff[slot] = out_dict[slot]
        else:
            # remove repeated first (check if MR has same val less than out + same value more than 1x)
            for val in out_dict[slot].keys():
                if val in mr_dict[slot] and mr_dict[slot][val] < out_dict[slot][val]:
                    repeated += out_dict[slot][val] - mr_dict[slot][val]
                    out_dict[slot][val] = mr_dict[slot][val]
            # now compute the diff in the # of value occurrences
            slot_diff = {val: mr_dict[slot].get(val, 0) - out_dict[slot].get(val, 0)
                         for val in set(mr_dict[slot].keys()) | set(out_dict[slot].keys())}
            diff[slot] = {val: -count for val, count in slot_diff.items() if count != 0}
            # diffs both ways
            mr_not_out = sum([count for count in slot_diff.values() if count > 0])
            out_not_mr = - sum([count for count in slot_diff.values() if count < 0])
            # value errors up to the same # of values
            valerr += min(mr_not_out, out_not_mr)
            # others fall under missing & added
            missing += max(mr_not_out - out_not_mr, 0)
            added += max(out_not_mr - mr_not_out, 0)

    diff = json.dumps({slot: vals for slot, vals in diff.items() if vals})
    return added, missing, valerr, repeated, diff


def process_file(filename, dump=None, out=sys.stdout):
    """Analyze a single file, optionally dump per-instance stats to a TSV.
    Will print to the `out` file provided (defaults to stdout)."""
    # read input from CSV or TSV
    with codecs.open(filename, 'r', 'UTF-8') as fh:
        line = fh.readline()
        sep = "\t" if "\t" in line else ","
    df = pd.read_csv(filename, sep=sep, encoding="UTF-8")
    # accept column names used in the dataset itself and in system outputs
    mr_col = 'MR' if 'MR' in df.columns else 'mr'
    ref_col = 'output' if 'output' in df.columns else 'ref'
    raw_mrs = list(df[mr_col])
    mrs = [DA.parse_diligent_da(mr) for mr in raw_mrs]  # parse MRs
    refs = list(df[ref_col])

    # count the statistics
    added, missing, valerr, repeated, mr_len, diffs = [], [], [], [], [], []
    tot_ok, tot_m, tot_a, tot_ma = 0, 0, 0, 0
    for mr, ref in zip(mrs, refs):
        # here's the main function where the texts are checked
        inst_a, inst_m, inst_v, inst_r, diff = check_output(mr, ref)
        # just add the totals
        if (inst_a and inst_m) or inst_v:
            tot_ma += 1
        elif inst_a or inst_r:
            tot_a += 1
        elif inst_m:
            tot_m += 1
        else:
            tot_ok += 1
        added.append(inst_a)
        missing.append(inst_m)
        valerr.append(inst_v)
        repeated.append(inst_r)
        diffs.append(diff)
        mr_len.append(len(mr))

    # print the statistics
    print(filename, file=out)
    print("A: %5d, M: %5d, V: %5d, R: %5d, L: %5d" %
          (sum(added), sum(missing), sum(valerr), sum(repeated), sum(mr_len)), file=out)
    semerr = (sum(added) + sum(missing) + sum(valerr) + sum(repeated)) / float(sum(mr_len))
    print("SemERR = %.4f" % semerr, file=out)
    print("InstOK : %5d / %5d = %.4f" % (tot_ok,  len(refs), tot_ok / float(len(refs))), file=out)
    print("InstAdd: %5d / %5d = %.4f" % (tot_a,  len(refs), tot_a / float(len(refs))), file=out)
    print("InstMis: %5d / %5d = %.4f" % (tot_m,  len(refs), tot_m / float(len(refs))), file=out)
    print("InstM+A: %5d / %5d = %.4f" % (tot_ma,  len(refs), tot_ma / float(len(refs))), file=out)

    # dump per-instance stats to TSV if needed
    if dump:
        df['added'] = added
        df['missing'] = missing
        df['valerr'] = valerr
        df['repeated'] = repeated
        df['mr_len'] = mr_len
        df['diff'] = diffs
        df.to_csv(dump, sep=b"\t", encoding='utf-8', index=False,
                  columns=[mr_col, ref_col, 'added', 'missing', 'valerr', 'repeated', 'mr_len', 'diff'])

    # return the stats for CSV stat output if multiple files are processed
    return {'filename': filename,
            'semerr': semerr,
            'added': sum(added),
            'missing': sum(missing),
            'valerr': sum(valerr),
            'repeated': sum(repeated),
            'total_attr': sum(mr_len),
            'total_insts': len(refs),
            'inst_ok': tot_ok / float(len(refs)),
            'inst_add': tot_a / float(len(refs)),
            'inst_mis': tot_m / float(len(refs)),
            'inst_m+a': tot_ma / float(len(refs)),}


if __name__ == '__main__':
    ap = ArgumentParser(description='Estimate semantic/slot error rate on E2E system outputs')
    ap.add_argument('--dump', '-d', type=str, help='Dump detailed output into a TSV file (one input only)')
    ap.add_argument('input_files', nargs='+', type=str, help='Input TSV file(s)')
    args = ap.parse_args()

    if len(args.input_files) == 1:
        process_file(args.input_files[0], args.dump)
    else:
        results = []
        for filename in args.input_files:
            results.append(process_file(filename, out=sys.stderr))
        results = pd.DataFrame.from_records(results)
        csv_out = results.to_csv(columns=['filename', 'total_insts', 'total_attr', 'semerr',
                                          'added', 'missing', 'valerr', 'repeated', 'inst_ok',
                                          'inst_add', 'inst_mis', 'inst_m+a'],
                                 index=False)
        print(csv_out)


