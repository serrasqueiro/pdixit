#-*- coding: utf-8 -*-
# pwordhash.sample.py  (c)2021  Henrique Moreira

"""
Dumps words hashes
"""

# pylint: disable=no-self-use, invalid-name

import sys
import os.path
from waxpage.redit import char_map
from xywinter.lehash import calc_p_hash, is_prime


ALPHABET_NUM = 1000
FIRST_PRIME_1000 = 1009		# First prime after 1000
DEFAULT_TWO_LETTER_LANG = "en"



def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    param = args
    if not param:
        param = [DEFAULT_TWO_LETTER_LANG]
    for nick in param:
        dump_nick(out, err, nick)
    return 0


def dump_nick(out, err, nick):
    """ Dumps file or nick. """
    opts = {
        "show-all": True,
        }
    # if nick is a two-letter, use e.g. ../../results/strict-pt.lst
    if len(nick) == 2 and nick.isalpha():
        fname = os.path.join("..", "..", "results", f"strict-{nick}.lst")
    else:
        fname = nick
    wset = dump_wordlist(out, err, nick, fname, ALPHABET_NUM, opts)
    queue = wset['queue']
    where, maxsize = wset['where'], wset['maxsize']
    for item in queue:
        hsh, shown = item
        if not shown:
            err.write(f"@ {hsh:>4} <empty>\n")
            continue
        out.write(f"@ {hsh:>4} {shown}\n")
    stats = wset['stats-bysize']
    for size in sorted(stats):
        print("# Stat:", size, stats[size])
    err.write(f"Maximum size for hash {where}: {maxsize}\n")


def dump_wordlist(out, err, nick:str, fname:str, arange:int, opts:dict) -> dict:
    """ Dumps hash for each word in a file. """
    enc = "ISO-8859-1"
    show_all = bool(opts.get("show-all"))
    queue, hshing = list(), list()
    wset = {
        'queue': queue,
        'hshing': hshing,
        'where': -1,
        'maxsize': -1,
        'hsh-capital': list(),	# hsh with (at least one) first letter capital
        'stats-bysize': dict(),
        }
    lines = open(fname, "r", encoding=enc).readlines()
    if nick:
        lst_exc_fname = os.path.join(os.path.dirname(fname), "exc-" + nick + ".lst")
        excl = from_exclusion_file(lst_exc_fname, enc)
    else:
        excl = from_exclusion_file()
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
        #if hsh != 269:
        #    continue
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
        queue.append((hsh, shown))
    infos, excluded = list(), excl['must']
    maxsize, where = -1, hsh
    # Stats
    wset['stats-bysize'][0] = 0
    for size in range(3, 7+1, 1):
        wset['stats-bysize'][size] = 0
    # Main loop
    for hsh in range(arange):
        idx = 0
        candidates = list()
        for size in range(3, 7+1, 1):
            words = bysize[size][hsh]
            if not words:
                continue
            rest = [word for word in words if word.islower() and not word in excluded]
            if not rest:
                continue
            if len(candidates) >= 3:
                continue
            candidates.append((size, hsh, rest))
        if candidates:
            size, hsh, rest = candidates[0]
            hshing.append(candidates[0])
            wset['stats-bysize'][size] += 1
            idx = size
            if idx > maxsize:
                maxsize, where = idx, hsh
        if idx <= 0:
            hshing.append((0, hsh, ["(NADA)"]))
            #out.write(f"bysize:- {hsh:>4} (NADA)\n")
            wset['stats-bysize'][0] += 1
    wset['hsh-capital'] = infos
    wset['where'], wset['maxsize'] = where, maxsize
    if not show_all:
        return wset
    # Dump if requested:
    for size, hsh, rest in hshing:
        shown = ";".join(rest)
        s_size = "-" if size == 0 else str(size)
        out.write(f"bysize:{s_size} {hsh:>4} {shown}\n")
    return wset


def valid_word(aword) -> str:
    """ Validate word, strictly """
    assert aword.isalpha()
    assert aword.strip() == aword
    return aword


def word_hash(astr) -> int:
    aval = calc_p_hash(astr, a_mod=FIRST_PRIME_1000) % 1000
    return aval


def from_exclusion_file(fname="", encoding="", debug=0) -> dict:
    """ Returns the dictionary of excluded words. """
    excl = {
        "must": dict(),
        }
    if not fname:
        return excl
    lines = open(fname, "r", encoding=encoding).readlines()
    words = [line.split("@")[0] for line in lines if not line.startswith("#")]
    for word in words:
        for a_chr in word:
            assert a_chr.isalpha() or ord(a_chr) >= 0xa0, f"Invalid char: {ord(a_chr)}d"
        excl['must'][word] = True
    if debug > 0:
        print("excl:", sorted(excl['must'], key=str.casefold))
    return excl


# Main script
if __name__ == "__main__":
    assert is_prime(FIRST_PRIME_1000)
    main()
