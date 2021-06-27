#-*- coding: ISO-8859-1 -*-
# whash.py  (c)2021  Henrique Moreira

"""
Word Hashes envelopes
"""

# pylint: disable=missing-function-docstring

FIX_VERSION = "V1"

class Envelope():
    """ Envelope abstract class. """
    _nick = ""
    _head = ""

    def __init__(self, nick:str="en", head=""):
        """ Initializer """
        self._nick = nick
        self._head = head

    def string(self) -> str:
        """ Returns the envelope string. """
        return self._head

class WHashEnvelope(Envelope):
    """ Word-Hash Envelope, for textual word hash text files (e.g. whash-en.txt) """
    def __init__(self, nick:str="en", alash=None, content:str=""):
        """ Initializer """
        super().__init__(nick)
        if alash:
            self.header_from_alash(alash, content)

    def header_from_alash(self, alash:dict, content:str):
        # pylint: disable=line-too-long
        wset = alash['wset']
        dotted = [str(wset['stats-bysize'][alen]) for alen in sorted(wset['stats-bysize']) if 3 <= alen <= 7]
        dotted_lens = '.'.join(dotted)
        if dotted_lens.endswith(".0"):
            dotted_lens = dotted_lens[:-2]
        stats = {
            "data-size": len(content),
            "#nwords": wset['nwords'],
            "#nwords-used": wset['nwords-used'],
            "#preferred-capital": len(wset['hsh-capital'][0]),
            "#len-dots": dotted_lens,
        }
        self._prepare_header(wset, stats)

    def _prepare_header(self, wset:dict, stats:dict):
        nick = self._nick
        assert nick
        fix = FIX_VERSION
        head = f"{nick}:{fix}.{stats['#nwords-used']}/{stats['#nwords']}"
        head += f".C{stats['#preferred-capital']}"
        head += f":{stats['#len-dots']}/{stats['data-size']}"
        self._head = f"# {head}"

# Main script
if __name__ == "__main__":
    print("Please import me.")
