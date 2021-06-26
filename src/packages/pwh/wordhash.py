#-*- coding: utf-8 -*-
# wordhash.py  (c)2021  Henrique Moreira

"""
Classes for Word Hashes
"""

# pylint: disable=unused-argument

import os.path
from xywinter.lehash import calc_p_hash, is_prime

ALPHABET_NUM = 1000
FIRST_PRIME_1000 = 1009		# First prime after 1000
DEFAULT_TWO_LETTER_LANG = "en"
KEEP_ROMANS_LANGS = ("zz",)   # Languages to keep Roman numbers

class WordSet():
    """ WordSet: class for word hashing statistics """
    _infos = None

    def __init__(self):
        """ Class initializer """
        self._infos = WordSet.infos_default()

    def stats(self):
        """ Returns current statistics """
        return self._infos

    @staticmethod
    def infos_default() -> dict:
        """ Returns default stats """
        infos = {
            'queue': list(),
            'hshing': list(),
            'where': -1,
            'nwords': 0,
            'nwords-used': 0,
            'maxsize': -1,
            'hsh-capital': list(),  # hsh with (at least one) first letter capital
            'bysize': list(),
            'stats-bysize': dict(),
            'excl': dict(),
        }
        return infos

class WordHash():
    """ WordHash class """
    def __init__(self, nick="", fname="", alpha_num=ALPHABET_NUM):
        """ Initializer """
        self.nick = nick
        self.fname = fname
        self.infos = WordSet()
        self.lines = list()
        self.excl = dict()
        self._criterias = default_wordset_criterias()
        assert alpha_num == ALPHABET_NUM, f"Invalid alpha_num: {alpha_num}"
        self._alpha_num = alpha_num

    def alpha_number(self):
        """ Returns ALPHABET NUM """
        return self._alpha_num

    def set_criterias(self, new:dict) -> bool:
        """ Set criterias (e.g. for not accumulating too many word alternatives """
        assert isinstance(new, dict)
        self._criterias = new
        is_ok = int(new["no-more-than"]) >= 3
        return is_ok

    def reader(self) -> bool:
        """ Reads dictionary content """
        enc = "ISO-8859-1"
        fname = self.fname
        lines = open(fname, "r", encoding=enc).readlines()
        if self.nick:
            lst_exc_fname = os.path.join(os.path.dirname(fname), "exc-" + self.nick + ".lst")
            excl = from_exclusion_file(lst_exc_fname, enc, self.nick)
        else:
            excl = from_exclusion_file()
        self.lines = lines
        self.excl = excl
        return bool(len(lines) > 0)

    def best_words(self, words:list, opt_hash:int=-1) -> list:
        """ Returns the 'best' words of a series of words """
        nwords, amax = len(words), self._criterias["no-more-than"]
        if nwords <= amax:
            return words
        simpler = words[:amax]
        return simpler

def from_exclusion_file(fname="", encoding="", nick:str="en", debug=0) -> dict:
    """ Returns the dictionary of excluded words. """
    reasons_why = dict()
    excl = {
        'must': dict(),
        '@used': dict(),
        'why': reasons_why,
        }
    if not fname:
        return excl
    data = open(fname, "r", encoding=encoding).read()
    lines = data.splitlines(keepends=False)
    words = list()
    for line in lines:
        if not valid_exclusion(line):
            continue
        tups = line.split("@", maxsplit=1)
        word = tups[0]
        words.append(word)
        reasons_why[word] = tups[1]
    if not nick in KEEP_ROMANS_LANGS:
        exclude_roman_numbers(words)
    for word in words:
        for a_chr in word:
            assert a_chr.isalpha() or ord(a_chr) >= 0xa0, f"Invalid char: {ord(a_chr)}d"
        excl['must'][word] = True
    if debug > 0:
        print("excl:", sorted(excl['must'], key=str.casefold))
    return excl

def exclude_roman_numbers(words) -> int:
    """ Extend words so that roman words are not hashed!
    """
    # pylint: disable=line-too-long
    count = 0
    # ("lvi", "lvii", "lxi", "lxii", "lxiv", "lxix", "lxvi", "lxvii")
    for item in (
        "lvi;lvii;lxi;lxii;lxiv;lxix;lxvi;lxvii",
        "vii;viii",
        "xi;xii;xiii;xis;xiv;xix",
        "xv;xvi;xvii;xviii;xx;xxi;xxii;xxiii;xxiv;xxix;xxv;xxvi;xxvii;xxviii;xxx;xxxi;xxxii;xxxiii;xxxiv;xxxix;xxxv;xxxvi;xxxvii;xxxviii",
        "xci;xcii;xciv;xcix;xcvi;xcvii",
        ):
        there = item.split(";")
        for word in there:
            assert word
            if word in words:
                continue
            if len(word) < 3:
                continue
            words.append(word)
        #words.extend(there)
        count += len(there)
    return count

def was_excluded(word:str, excluded:dict, excl:dict) -> bool:
    """ Returns True if the word is part of the excluded words.
    """
    used = excl['@used']
    if not word in excluded:
        return False
    if word in used:
        used[word] += 1
    else:
        used[word] = 1
    return True

def valid_word(aword) -> str:
    """ Validate word, strictly """
    assert aword.isalpha()
    assert aword.strip() == aword
    return aword

def valid_exclusion(astr:str) -> bool:
    """ Returns True if 'astr' is a valid exclusion string.
    """
    if astr.startswith("#"):
        return False
    bare = astr.replace("-", "").split("@")
    assert 0 < len(bare) <= 2, f"Invalid exclusion string (1): '{astr}'"
    new = "".join(bare)
    assert new.isalpha(), f"Invalid exclusion string (2): '{astr}' >>>{new}<<<"
    return True

def word_hash(astr) -> int:
    """ Returns the word hash ('astr' should be simple letter string!) """
    aval = calc_p_hash(astr, a_mod=FIRST_PRIME_1000) % 1000
    return aval

def default_wordset_criterias() -> dict:
    """ Returns the default criteria """
    crit = {
        "no-more-than": 6,  # up to 5 words on a single hash
    }
    return crit

def nick_from_name(name:str, suffix:str=".lst") -> str:
    """ Get language nick from a filename
    :param name: name - full path name of a file (default extension: .lst)
    :param suffix: extension
    :return: the (two-letter) language nick
    """
    if not name.endswith(suffix):
        return ""
    subname = name.replace("\\", "/").split("/")[-1]
    astr = subname[:-len(suffix)].split("-")[-1]
    return astr

def valid_nick(nick:str) -> bool:
    """ Returns True if 'nick' is a valid language nick """
    is_ok = len(nick) == 2 and nick.isalpha()
    return is_ok

# Main script
if __name__ == "__main__":
    assert is_prime(FIRST_PRIME_1000)
    print("Please import me.")
