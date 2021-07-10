#!/usr/bin/python3
#-*- coding: utf-8 -*-
# tinycheck.py  (c)2021  Henrique Moreira

"""
Pre-checks existing data
"""

# pylint: disable=missing-docstring

import sys
import json
import tabular.csv

F_STATES_HASH = "using/states_hash.json"
F_BABY_BY_STATE = "data-babynames/baby-names-by-state.csv"


def main():
    """ Main function """
    prog = __file__
    code = run(sys.stdout, sys.stderr, sys.argv[1:])
    if code < 0:
        print(f"""Usage:
  {prog}

Without args:
  - checks data consistency within ../names/ directory.
""")
    sys.exit(0 if code < 0 else code)

def run(out, err, args:list) -> int:
    """ Main run """
    assert out
    if args:
        return -1
    opts = {
        'states-json': F_STATES_HASH,
        'by-state-csv': F_BABY_BY_STATE,
        '@out': dict(),
    }
    msg = checker(opts)
    result = opts['@out']
    assert result
    if msg:
        if err:
            err.write(f"Failed: {msg}\n")
    return 0

def checker(opts:dict) -> str:
    """ Checks data/ file consistency.
    Filenames (and paths) are hard-coded -- it is intended to be simple.
    """
    jfname = opts['states-json']
    adict = json.load(open(jfname, "r"))
    assert isinstance(adict, dict), f"Expected to be a dictionary, but got: {type(adict)}"
    states = adict
    csv_state = opts['by-state-csv']
    stt = tabular.csv.CSV(csv_state)
    tidy_by_state(stt, states)
    return ""

def tidy_by_state(stt, states) -> str:
    for idx, tup in stt.rows:
        assert idx > 0
        abbrev, year, name, count, boy = tup
        if name == "\xa0":
            print(":::", idx, year)
        if abbrev not in states:
            return f"Invalid state abbreviation, line {idx}: '{abbrev}'"
    return ""

if __name__=="__main__":
    main()
