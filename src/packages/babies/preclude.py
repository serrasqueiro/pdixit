#-*- coding: utf-8 -*-
# preclude  (c)2021  Henrique Moreira

"""
Basic math functions to handle baby data.
"""

# pylint: disable=unused-argument

def precluded_name(astr:str="") -> list:
    """ Relatively short name with names precluded, or
    """
    noname = (
        "Unknown",
        "Unnamed",
        "Notnamed",
    )
    if not astr:
        return sorted(noname)
    return astr in noname

# Main script
if __name__ == "__main__":
    print("Please import me.")
