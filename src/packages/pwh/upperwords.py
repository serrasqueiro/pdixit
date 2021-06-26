#-*- coding: utf-8 -*-
# upperwords.py  (c)2021  Henrique Moreira

"""
Fixed list of upper-case words
"""

# pylint: disable=missing-function-docstring, line-too-long

UPPERCASE_VALID = (
    "Cuba",
    "Romeu",
)

ROMAN_SEQS = (
    "lvi;lvii;lxi;lxii;lxiv;lxix;lxvi;lxvii",
    "vii;viii",
    "xi;xii;xiii;xis;xiv;xix",
    "xv;xvi;xvii;xviii;xx;xxi;xxii;xxiii;xxiv;xxix;xxv;xxvi;xxvii;xxviii;xxx;xxxi;xxxii;xxxiii;xxxiv;xxxix;xxxv;xxxvi;xxxvii;xxxviii",
    "xci;xcii;xciv;xcix;xcvi;xcvii",
    )


class AnyCache():
    """ Any Cache class (abstract) """
    _name = ""
    _cache = None

    def clean(self):
        """ Clear cache """
        self._cache = dict()

class WordsCache(AnyCache):
    """ Words Cache """
    def __init__(self, name="up"):
        self._name = name
        self._cache = dict()

    def named(self) -> str:
        return self._name

    def cache(self) -> dict:
        if not self._cache:
            self._build_cache(UPPERCASE_VALID)
        return self._cache

    def _build_cache(self, words:list, value:int=1):
        for word in words:
            self._cache[word] = value

def valid_uppercase_word(astr:str) -> bool:
    """ Returns True if word is a valid upper-case word.
    We do not check here the entire string, just against a
    pre-defined cache (wcache, a WordsCache).
    """
    if not astr:
        return False
    return astr in wcache.cache()

# Singleton
wcache = WordsCache("upper-case-words")

# Main script
if __name__ == "__main__":
    print("Please import me.")
