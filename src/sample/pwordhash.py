#-*- coding: utf-8 -*-
# pwordhash.py  (c)2021  Henrique Moreira

"""
Dumps words hashes
"""

# pylint: disable=no-self-use, invalid-name

import sys
import os.path
from waxpage.redit import char_map
import pwh.wordhash as wordhash


DEBUG = 0


def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""pwordhash.py [options] [language]

Language is either two letter ('en', 'pt', 'fr', ...) or full path for an 'strict-??.lst' file.

Options are:
   -v      Verbose; dump also dialet (@...hashes)
""")
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    debug = DEBUG
    param = args
    opts = {
        "show-all": True,
        "show-data": False,
        }
    while param and param[0].startswith('-'):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            opts["show-data"] = True
            continue
        return None
    if not param:
        param = [wordhash.DEFAULT_TWO_LETTER_LANG]
    for nick in param:
        dump_nick(out, err, nick, opts, debug)
    return 0


def dump_nick(out, err, nick, opts, debug=0) -> int:
    """ Dumps file or nick. """
    show_data = bool(opts.get("show-data")) and out
    # if nick is a two-letter, use e.g. ../../results/strict-pt.lst
    if len(nick) == 2 and nick.isalpha():
        fname = os.path.join("..", "..", "results", f"strict-{nick}.lst")
    else:
        fname = nick
    whash = wordhash.WordHash(nick)
    whash.fname = fname
    wset = dump_wordlist(out, err, whash, opts)
    queue = wset['queue']
    where, maxsize = wset['where'], wset['maxsize']
    for item in queue:
        hsh, shown = item
        if not shown:
            err.write(f"@ {hsh:>4} <empty>\n")
            continue
        if show_data:
            out.write(f"@ {hsh:>4} {shown}\n")
    stats = wset['stats-bysize']
    for size in sorted(stats):
        shown = f"{stats[size]}"
        if size <= 0:
            shown = f"{stats[size]}" if stats[size] else "0 (OK)"
        print(f"# Stat size={size} {shown}")
    # Dump exclusions not used
    d_usage = wset['excl']['@used']
    for word in sorted(wset['excl']['must'], key=str.casefold):
        if not word in d_usage:
            err.write(f"# Warn: Unused exclusion: {word}\n")
    # Dump final stat
    err.write(f"Maximum size for hash {where}: {maxsize}\n")
    s_stat = f"queue#={len(wset['queue'])}"
    s_stat += f", maxsize={wset['maxsize']}"
    s_stat += f", nwords={wset['nwords']}"
    s_stat += f", used words={wset['nwords-used']}"
    if debug > 0:
        err.write(f"""
fname='{fname}'
{s_stat}

d_usage: {d_usage}\n<--
""")
    return 0


def dump_wordlist(out, err, whash, opts:dict) -> dict:
    """ Dumps hash for each word in a file. """
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
    assert last
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


# Main script
if __name__ == "__main__":
    main()
