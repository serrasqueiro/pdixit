#-*- coding: utf-8 -*-
# pwordhash.sample.py  (c)2021  Henrique Moreira

"""
Dumps words hashes
"""

# pylint: disable=no-self-use, invalid-name

import sys
import os.path
from waxpage.redit import char_map
from xywinter.lehash import calc_p_hash


ALPHABET_NUM = 1000
FIRST_PRIME_1000 = 1009		# First prime after 1000



def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    param = args
    for nick in param:
        dump_nick(out, err, nick)
    return 0


def dump_nick(out, err, nick):
    """ Dumps file or nick. """
    # if nick is a two-letter, use e.g. ../../results/strict-pt.lst
    if len(nick) == 2 and nick.isalpha():
        fname = os.path.join("..", "..", "results", f"strict-{nick}.lst")
    else:
        fname = nick
    dump_wordlist(out, err, fname, ALPHABET_NUM)


def dump_wordlist(out, err, fname, arange, show_all=True) -> bool:
    """ Dumps hash for each word in a file. """
    enc = "ISO-8859-1"
    lines = open(fname, "r", encoding=enc).readlines()
    words = [valid_word(word.rstrip('\n')) for word in lines if not word.startswith('#')]
    dct, bysize = dict(), dict()
    for size in range(3, 7+1, 1):
        bysize[size] = dict()
        for hsh in range(arange):
            bysize[size][hsh] = list()
    for hsh in range(arange):
        dct[hsh] = list()
    last = ""
    for aword in words:
        word = char_map.simpler_ascii(aword, 1)
        s_word = char_map.simpler_ascii(aword)
        hsh = word_hash(word)
        dct[hsh].append((word, s_word))
        last = s_word
        size = len(s_word)
        if not size:
            continue
        if 3 <= size <= 7:
            bysize[size][hsh].append(s_word)
        # f"{hsh:>4} {word}\n")
        #if s_word < last:
        #    err.write(f"Word '{s_word}' is not sorted alphabetically (last was '{last}')\n")
    assert last
    for hsh in range(arange):
        words = dct[hsh]
        shown = ';'.join([word for word, _ in words])
        out.write(f"@ {hsh:>4} {shown}\n")
    if not show_all:
        return True
    maxsize, where = -1, hsh
    for hsh in range(arange):
        idx = 0
        for size in range(3, 7+1, 1):
            words = bysize[size][hsh]
            if not words:
                continue
            shown = ';'.join([word for word in words])
            out.write(f"bysize:{size} {hsh:>4} {shown}\n")
            idx = size
            if idx > maxsize:
                maxsize, where = idx, hsh
            break
        if idx <= 0:
            out.write(f"bysize:- {hsh:>4} (NADA)\n")
    err.write(f"Maximum size for hash {where}: {maxsize}\n")
    return True


def valid_word(aword) -> str:
    assert aword.isalpha()
    assert aword.strip() == aword
    return aword


def word_hash(astr) -> int:
    aval = calc_p_hash(astr, a_mod=FIRST_PRIME_1000) % 1000
    return aval




# Main script
if __name__ == "__main__":
    main()
    assert is_prime(_FIRST_PRIME_1000)
    assert next_prime(_ALPHABET_NUM) == _FIRST_PRIME_1000
