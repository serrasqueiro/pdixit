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
        '@out': default_out_dict(),
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
    dbd = [states, opts['@out']]
    tidy_by_state(stt, states, dbd)
    return ""

def tidy_by_state(stt, states, dbd) -> str:
    by_year = dict()
    for idx, tup in stt.rows:
        assert idx > 0
        abbrev, year, name, count, boy = tup
        if name == "\xa0" or count in ("NA",):
            continue
        if abbrev not in states:
            return f"Invalid state abbreviation, line {idx}: '{abbrev}'"
        if boy in ("boy", "girl"):
            boy = boy == "boy"
        else:
            return f"Invalid genre, line {idx}: {tup}"
        genre = "m" if boy else "f"
        year = int(year)
        count = int(count)
        data = [name, genre, count]
        if year not in by_year:
            by_year[year] = dict()
        key = f"{genre}:{name}"
        if key in by_year[year]:
            by_year[year][key][2] += count
        else:
            by_year[year][key] = data
    if dbd:
        dbd[1]['by-year'] = by_year
    return ""

def default_out_dict() -> dict:
    adict = {
        'by-year': dict(),
    }
    return adict

if __name__=="__main__":
    main()
