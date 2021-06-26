#-*- coding: ISO-8859-1 -*-
# wordhashf.py  (c)2021  Henrique Moreira

"""
Word Hashes functions/ utilities
"""

# pylint: disable=unused-argument

import pwh.wordhash as wordhash
import pwh.upperwords as upperwords
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
        # *if* hsh in (63, 104) and word.startswith("ch") ...; cha~ vs cha'
        hsh = wordhash.word_hash(s_word)
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
    info_up, excluded = list(), whash.excl['must']
    info_up += [list(), dict()]
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
            rest, up_words = list(), list()
            for word in words:
                if word.islower():
                    if not wordhash.was_excluded(word, excluded, whash.excl):
                        if word not in rest:
                            rest.append(word)
                elif upperwords.valid_uppercase_word(word):
                    up_words.append((word, 1))
                elif word[1:].islower():
                    up_words.append((word, 1 + len(word)))
            if not rest:
                if not up_words:
                    continue
                for word, up_kind in up_words:
                    tofu = {'hsh': hsh, 'size': size, 'word': word, 'kind': up_kind,
                            }
                    info_up[0].append(tofu)
                    if hsh in info_up[1]:
                        info_up[1][hsh].append(tofu)
                    else:
                        info_up[1][hsh] = [tofu]
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
    wset['hsh-capital'] = info_up
    wset['where'], wset['maxsize'] = where, maxsize
    wset['wthere'] = dict() # wset['hshing'][915] = ['word1', 'word2', ...]; here indexes a word to its hash
    iterate_wording(wset['hshing'], wset['wthere'])
    word_sub_info_upper(info_up, wset)
    if show_all:
        word_subcalc(out, whash, hshing, wset)
    return wset

def iterate_wording(hshing:list, wthere:dict):
    """ Updates word-to-hash ('wthere') """
    for _, hsh, wordlist in hshing:
        for word in wordlist:
            assert not word in wthere, f"Duplicate word for hsh={hsh}, '{word}' (there: {wthere[word]})"
            wthere[word] = hsh

def word_subcalc(out, whash, hshing, wset:dict):
    """ Dump and/ or calculate nwords-used. """
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

def word_sub_info_upper(info_up, wset:dict):
    """ Check if there is any gain by using upper-case words """
    # e.g. wset['bysize'][915] = 'bysize:6  915 agrido;burlar;cofiar;cometa;finito;houver'
    # by using word 'Midas', this reduces to 'bysize:5  915 Midas'
    _, updict = info_up
    uppers = list()
    for akind in (1, 6,):
        prios = list()
        for hsh, alist in updict.items():
            for this in alist:
                word, kind = this['word'], this['kind']
                if kind != akind:
                    continue
                if word.lower() in wset['wthere']:
                    continue
                prios.append(this)
        for this in prios:
            hsh, size, word = this['hsh'], this['size'], this['word']
            there = wset['hshing'][hsh]
            size_there = there[0]
            if size >= size_there:
                continue
            if akind >= 6 and size + 1 >= size_there:
                # Not worthwhile using this (word starting with upper-case is only slightly shorter (1 char only!)
                continue
            there = (size, hsh, [word])
            assert word not in wset['wthere'], f"Unexpected word in the existing word-to-hash: '{word}'"
            wset['wthere'][word] = hsh
            wset['hshing'][hsh] = there
            uppers.append(there)
    info_up[0] = uppers
    return uppers

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
