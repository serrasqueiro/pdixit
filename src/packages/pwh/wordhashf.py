#-*- coding: utf-8 -*-
# wordhashf.py  (c)2021  Henrique Moreira

"""
Word Hashes functions/ utilities
"""

# pylint: disable=unused-argument

import pwh.wordhash as wordhash
from waxpage.redit import char_map

def dump_wordlist(out, err, whash, opts:dict) -> dict:
    """ Dumps hash for each word in a file. """
    # pylint: disable=line-too-long
    show_all = bool(opts.get("show-all"))
    wset = whash.infos.stats()
    queue, hshing = wset['queue'], wset['hshing']
    arange = whash.alpha_number()
    assert arange >= 10, f"alpha_number() is usually 1000; at least 10; got {arange}"
    whash.reader()
    wset = whash.infos.stats()
    wset['excl'] = whash.excl
    words = [wordhash.valid_word(word.rstrip('\n')) for word in whash.lines if not word.startswith('#')]
    dct, bysize = dict(), dict()
    for size in range(3, 7+1, 1):
        bysize[size] = dict()
        for hsh in range(arange):
            bysize[size][hsh] = list()
    for hsh in range(arange):
        dct[hsh] = list()
    last = ""
    wset['nwords'] = len(words)
    for aword in words:
        word = char_map.simpler_ascii(aword, 1)
        s_word = char_map.simpler_ascii(aword)
        hsh = wordhash.word_hash(word)
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
    fname = whash.fname
    if not last:
        err.write(f"Invalid: {fname}\n")
        return wset
    for hsh in range(arange):
        words = dct[hsh]
        shown = ';'.join([word for word, _ in words])
        queue.append((hsh, shown))
    infos, excluded = list(), whash.excl['must']
    maxsize, where = -1, 0
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
            rest = list()
            for word in words:
                if word.islower() and not wordhash.was_excluded(word, excluded, whash.excl):
                    rest.append(word)
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
    for size, hsh, words in hshing:
        rest = whash.best_words(words, hsh)
        wset['nwords-used'] += len(rest)
        shown = ";".join(rest)
        s_size = "-" if size == 0 else str(size)
        shown = f"bysize:{s_size} {hsh:>4} {shown}"
        if out:
            out.write(f"{shown}\n")
        else:
            wset['bysize'].append(shown)
    return wset

def wset_words(wset, err=None) -> list:
    """ Dumps and sets"""
    data = list()
    n_errs = 0
    by_len = len("bysize:N")
    for item in wset['bysize']:
        if item[by_len-1] == "-":
            n_errs += 1
            if err:
                err.write(f"Missing letter hash: {item}\n")
            continue
        astr = item[by_len+2:]
        data.append(astr)
    if n_errs <= 0:
        return data
    err.write(f"#missing letter hashes: {n_errs}\n")
    return list()

# Main script
if __name__ == "__main__":
    print("Please import me.")
