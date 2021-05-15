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
        shown = f"{stats[size]}"
        if size <= 0:
            shown = f"{stats[size]}" if stats[size] else "0 (OK)"
        print(f"# Stat size={size} {shown}")
    # Dump exclusions not used
    idx = 0
    for word in sorted(wset['excl']['must'], key=str.casefold):
        if not word in wset['excl']['@used']:
            err.write(f"# Warn: Unused exclusion: {word}\n")
    # Dump final stat
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
        'bysize': list(),
        'stats-bysize': dict(),
        'excl': dict(),
        }
    lines = open(fname, "r", encoding=enc).readlines()
    if nick:
        lst_exc_fname = os.path.join(os.path.dirname(fname), "exc-" + nick + ".lst")
        excl = from_exclusion_file(lst_exc_fname, enc, nick)
    else:
        excl = from_exclusion_file()
    wset['excl'] = excl
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
            rest = [word for word in words if word.islower() and not was_excluded(word, excluded, excl)]
            if not rest:
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
        shown = f"bysize:{s_size} {hsh:>4} {shown}"
        if out:
            out.write(f"{shown}\n")
        else:
            wset['bysize'].append(shown)
    return wset


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
    aval = calc_p_hash(astr, a_mod=FIRST_PRIME_1000) % 1000
    return aval


def from_exclusion_file(fname="", encoding="", nick:str="en", debug=0) -> dict:
    """ Returns the dictionary of excluded words. """
    excl = {
        'must': dict(),
        '@used': dict(),
        }
    if not fname:
        return excl
    data = open(fname, "r", encoding=encoding).read()
    lines = data.splitlines(keepends=False)
    words = [line.split("@")[0] for line in lines if valid_exclusion(line)]
    if nick == "en":
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
    count = 0
    # ("lvi", "lvii", "lxi", "lxii", "lxiv", "lxix", "lxvi", "lxvii")
    for item in (
        "lvi;lvii;lxi;lxii;lxiv;lxix;lxvi;lxvii",
        "xi;xii;xiii;xis;xiv;xix",
        "xv;xvi;xvii;xviii;xx;xxi;xxii;xxiii;xxiv;xxix;xxv;xxvi;xxvii;xxviii;xxx;xxxi;xxxii;xxxiii;xxxiv;xxxix;xxxv;xxxvi;xxxvii;xxxviii",
        ):
        there = item.split(";")
        for word in there:
            assert word
            assert word not in words, f"Duplicate exclusion: {word}"
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
    assert not word in used, f"Duplicate: {word}"
    if word in used:
        used[word] += 1
    else:
        used[word] = 1
    return True


# Main script
if __name__ == "__main__":
    assert is_prime(FIRST_PRIME_1000)
    main()
