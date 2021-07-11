#-*- coding: utf-8 -*-
# dataconv.py  (c)2021  Henrique Moreira

"""
Generic data conversion, e.g. from dict() to list()
"""

# pylint: disable=missing-function-docstring

def to_list(adict:dict, first:int=1, there:str="There") -> list:
    """ Generic function to convert a dictionary into a list,
    ordered alphabetically.
    """
    if isinstance(adict, tuple):
        return list(tuple)
    if isinstance(adict, list):
        return adict
    assert isinstance(adict, dict)
    akeys = sorted(adict, key=str.casefold)
    idx = first
    result = list()
    assert there not in (
        "Id", "Name",
    )
    if there:
        s_there = there
    else:
        s_there = "There"
    for key in akeys:
        content = adict[key]
        item = {"Id": idx, "Name": key, s_there: content}
        result.append(item)
        idx += 1
    return result

def keys(obj, defaults:str="a") -> list:
    """ Returns the list of keys of an object.
    Dictionary - returns the keys()
    List - returns the easiest set
    Int/ Float - list with one string
    """
    if obj is None:
        return list()
    if isinstance(obj, dict):
        if not defaults:
            return obj.keys()
        if defaults == "A":
            return sorted(obj.keys(), key=str.casefold)
        if defaults == "a":
            return sorted(obj.keys())
        if defaults == "d":
            return sorted(obj.keys(), reverse=True)
        assert False, f"Invalid value for defaults: {defaults}"
    if isinstance(obj, (list, tuple)):
        return list(set(sorted(obj)))
    if isinstance(obj, (str, int, float)):
        return [f"{obj}"]
    return list()

# Main script
if __name__ == "__main__":
    print("Please import me.")
