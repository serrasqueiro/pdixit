#-*- coding: ISO-8859-1 -*-
# whashr.py  (c)2021  Henrique Moreira

"""
Word Hashes text-file reader!
"""

# pylint: disable=missing-function-docstring

FIX_VERSION = "V1"

DEF_ENCODING = "ISO-8859-1"
WHASH_ENCODING = DEF_ENCODING

class TxIO():
    """ Text-like Input/ Output abstract class. """
    _msg = ""
    _data = ""

    def string(self) -> str:
        """ Returns the file content as a string. """
        return self._data

class Words(TxIO):
    """ Simple text-file reader """
    def __init__(self, nick:str="en"):
        """ Initializer """
        self._nick = nick
        self._msg, self._data = "", ""
        self._size = 0
        self.words = list()

    def reader(self, whash_fname:str) -> bool:
        version = FIX_VERSION
        nick = self._nick
        assert nick
        data = open(whash_fname, "r", encoding=WHASH_ENCODING).readlines()
        header, tail = data[0], data[1:]
        self._msg = "Failed: '{whash_fname}'"
        self._data, self.words = "", list()
        if not header.startswith(f"# {nick}:{version}"):
            return False
        size = int(header.split("/")[-1])
        self._size = size
        if size != len(tail):
            self._msg = f"header size mismatches payload size: {len(tail)}"
        self._msg = ""
        for line in tail:
            self.words.append(line.strip().split(" "))
            self._data += line
        return True

# Main script
if __name__ == "__main__":
    print("Please import me.")
    # wht = Words("en"); wht.reader("../results/whash-en.txt")
