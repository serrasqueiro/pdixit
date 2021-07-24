#-*- coding: utf-8 -*-
# textdict.test.py  (c)2021  Henrique Moreira

"""
Tests textdict.py
"""

# pylint: disable=missing-function-docstring

import sys
import dtable.textdict

TEXT_ALIKE = (
    ".txt",
    ".mi",
)


def main():
    run_tests(sys.stdout, sys.stderr, sys.argv[1:])

def run_tests(out, err, args):
    default_test_file = __file__
    param = args if args else [default_test_file]
    code = testers(out, err, param)
    assert code == 0

def testers(out, err, file_list:list) -> int:
    for fname in file_list:
        if tester(out, err, fname):
            return 1
    return 0

def tester(out, err, fname:str) -> int:
    """ A simple test:
    1. Single-keyed text-file input.
    Assumes text-file 'fname' has a header '# column-a;column-b'
    """
    is_txt = fname.endswith(TEXT_ALIKE)
    print("Reading:", fname)
    tdt = dtable.textdict.TextDict(fname)
    is_ok = tdt.reader()
    hint = f" (used encoding='{tdt.io_encoding()}'"
    if not is_ok:
        msg = tdt.last_error()
        err.write(f"Encoding read failed: {fname}{hint}: {msg}\n")
        return 1
    n_keys = 1 if is_txt else 0
    tdt.to_dict(lead_keys=n_keys)
    msg = tdt.last_error()
    print(f"tdt.get_dict(), lead_keys={n_keys}:")
    adict = tdt.get_dict()
    if msg:
        err.write(f"Bogus: {fname}: {msg}\n")
        return 4
    for key in sorted(adict):
        print(key, adict[key])
    print("--+++ JSON! +++--->")
    out.write(tdt.json_string())
    print("<-+++ (END) +++---")
    return 0

# Main script
if __name__ == "__main__":
    main()
