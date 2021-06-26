#-*- coding: utf-8 -*-
# upperwords.py  (c)2021  Henrique Moreira

"""
Fixed list of upper-case words
"""

# pylint: disable=unused-argument

UPPERCASE_VALID = (
    "Cuba",
    "Romeu",
)

class AnyCache():
    _name = ""
    _cache = None

    def clean(self):
        """ Clear cache """
        self._cache = dict()

class WordsCache(AnyCache):
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
    if not astr:
        return False
    return astr in wcache.cache()

# Singleton
wcache = WordsCache("upper-case-words")

# Main script
if __name__ == "__main__":
    print("Please import me.")
