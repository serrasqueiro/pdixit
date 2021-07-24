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
    _extra = None

    def string(self) -> str:
        """ Returns the file content as a string. """
        return self._data

    def last_error(self) -> str:
        """ Returns the last-error string. """
        return self._msg

class Words(TxIO):
    """ Simple text-file reader """
    def __init__(self, nick:str="en"):
        """ Initializer """
        self._nick = nick
        self._msg, self._data = "", ""
        self._size = 0
        self.words, self._extra = list(), list()
        assert len(nick) >= 2 or nick in ("*",)

    def language_nick(self) -> str:
        """ Returns the language nick, e.g. 'en'
        """
        assert self._nick
        return self._nick

    def reader(self, whash_fname:str="", stream=None) -> bool:
        version = FIX_VERSION
        nick = self._nick
        assert nick
        if whash_fname:
            data = open(whash_fname, "r", encoding=WHASH_ENCODING).readlines()
            assert stream is None
        else:
            assert stream is not None
            data = stream.readlines()
        header, tail = data[0], data[1:]
        self._msg = f"Failed: '{whash_fname}'"
        self._data, self.words = "", list()
        if nick in ("*",):
            if not header.startswith("# "):
                return False
            nick = header[1:].strip().split(":")[0]
            assert nick != self._nick
            self._nick = nick
        else:
            if not header.startswith(f"# {nick}:{version}"):
                return False
        size = int(header.split("/")[-1])
        self._size = size
        if size != len(tail):
            self._msg = f"header size mismatches payload size: {len(tail)}"
        self._msg = ""
        extra = None
        for line in tail:
            if line.startswith("#"):
                assert extra is None
                extra = list()
                continue
            within = line.strip().split(" ")
            if extra is None:
                self.words.append(self._clip_whash_list(within))
            else:
                ascii_idx = within[0]
                if ascii_idx.endswith("d") and ascii_idx[:-1].isdigit():
                    num = int(ascii_idx[:-1])
                else:
                    num = 0
                extra.append((num, [word.strip(';') for word in within[1:]]))
            self._data += line
        self._extra = extra
        return True

    def _clip_whash_list(self, pair:list) -> list:
        """ Usually 'pair' is a list with two elements,
		e.g. ['yam', '500']; but 'ascii' whash'es have 3 elements;
		e.g. ['yards', '114', 'r']
        """
        assert isinstance(pair, (tuple, list))
        assert 2 <= len(pair) <= 3, f"Invalid pair: {pair}"
        res = pair[:2]	# Two elements
        return res

class WordsA(Words):
    def get_extra(self) -> list:
        """ Returns _extra -- the lines after '# ASCII', for e.g. 'whash-en-ascii.txt'
        """
        return self._extra

    def get_extra_dict(self) -> dict:
        """ Returns the indexing of ASCII to letters, as a dictionary.
        """
        res = dict()
        if self._extra is None:
            return res
        for num, within in self._extra:
            assert num not in res, f"Duplicate ascii_idx: {num}d"
            res[num] = within[1:]
        return res

# Main script
if __name__ == "__main__":
    print("Please import me.")
    # wht = Words("en"); wht.reader("../results/whash-en.txt")
