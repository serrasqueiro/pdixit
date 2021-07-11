#-*- coding: utf-8 -*-
# test.py  (c)2021  Henrique Moreira

"""
Testing babies.yearlynames.py and such!
"""

# pylint: disable=missing-function-docstring

import sys
import babies.yearlynames as yearlynames
import pwh.dataconv as dataconv

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
    code, jby, alist, yearly = outs
    assert alist
    print("Keys:", dataconv.keys(yearly))
    show_pop(1983, jby)
    show_pop(2005, jby)
    return code

def show_pop(year:int, jby):
    print("Show (10) most popular names of year:", year)
    idx = 0
    for male, female in jby.top10(year):
        idx += 1
        print(f"#{idx:<2} {male:<20} {female:<20}.")

def run(out:None, args) -> tuple:
    assert out
    fname = args[0] if args else "gather/us/names-by-year.csv"
    # ../../../names/gather/us/names-by-year.csv
    jby = yearlynames.ByYear(fname, "names-by-year")
    jby.reader()
    outs = (0, jby, jby.listing(), jby.popular())
    return outs

# Main script
if __name__ == "__main__":
    main()
