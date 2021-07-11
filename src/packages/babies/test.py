#-*- coding: utf-8 -*-
# test.py  (c)2021  Henrique Moreira

"""
Testing babies.yearlynames.py and such!
"""

# pylint: disable=missing-function-docstring

import sys
import babies.yearlynames as yearlynames

def main():
    """ Main script! """
    prog = __file__
    code = tester(sys.argv[1:])
    if code < 0:
        print(f"""Usage:
python3 {prog} [file(s)]
""")
    sys.exit(0 if code < 0 else code)

def tester(args=None) -> int:
    outs = run(sys.stdout, args if args else [])
    code, alist = outs
    return code

def run(out:None, args) -> tuple:
    assert out
    fname = args[0] if args else "gather/us/names-by-year.csv"
    jby = yearlynames.ByYear(fname, "names-by-year")
    jby.reader()
    outs = (0, jby.listing())
    return outs

# Main script
if __name__ == "__main__":
    main()
