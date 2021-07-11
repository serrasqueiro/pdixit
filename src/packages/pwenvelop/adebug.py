#-*- coding: ISO-8859-1 -*-
# adebug.py  (c)2021  Henrique Moreira

"""
A tiny debug module!
"""

DEBUG = 0

def dprint(what:str, *rest) -> bool:
    """ Only prints (to stdout) if DEBUG is > 0, or if 'what' string is not empty.
    """
    if DEBUG <= 0:
        return False
    if not what:
        return False
    print(*rest)
    return True

def has_debug() -> bool:
    """ Returns True if DEBUG was defined (>0). """
    return int(DEBUG) > 0

# Main script
if __name__ == "__main__":
    print("Please import me.")
