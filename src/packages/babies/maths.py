#-*- coding: utf-8 -*-
# maths  (c)2021  Henrique Moreira

"""
Basic math functions to handle baby data.
"""

import operator

# pylint: disable=unused-argument

def from_permil(astr:str) -> float:
    """ Converts percentage or permil into a float (usually between 0 and 1!)
    """
    if isinstance(astr, (int, float)):
        return float(astr)
    assert isinstance(astr, str), "from_permil(), not a string"
    if astr == "-":
        return 0.0
    if astr.endswith("%"):
        conv = float(astr[:-1]) / 100.0
    elif astr.endswith("%o"):
        conv = float(astr[:-2]) / 1000.0
    else:
        conv = float(astr)
    return conv

def descending_ratio(adict:dict) -> list:
    """ Returns a list with descending order of floats.
    """
    an_order = True
    asort = sorted(adict.items(), key=operator.itemgetter(1), reverse=an_order)
    return asort

# Main script
if __name__ == "__main__":
    print("Please import me.")
