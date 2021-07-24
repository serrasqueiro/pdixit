#-*- coding: utf-8 -*-
# sampler.py  (c)2021  Henrique Moreira

"""
Various utilities around word hashing (and 'whash' files).
"""

# pylint: disable=missing-function-docstring

import sys
import pwh.wordhash as wordhash
import pwenvelop.whashr
import pwenvelop.adebug
from pwenvelop.adebug import dprint
import babies.yearlynames as yearlynames
import babies.maths
import babies.preclude

FULL_DEBUG = 0


def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""sampler.py COMMAND [options] [file(s)]

Commands are:
   check      Basic whash-??.txt -- check whash-file(s)

   names      Basic names-by-year.csv check; must specify csv and whash-file(s)
              Use @ to designate defaults.

Options are:
   -v      Verbose
""")
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    code = None
    if not args:
        return None
    opts = {
        "verbose": 0,
    }
    cmd, param = args[0], args[1:]
    while param and param[0].startswith('-'):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            opts["verbose"] += 1
            continue
        return None
    verbose = opts["verbose"]
    if verbose >= 3:
        pwenvelop.adebug.DEBUG = 1
    if cmd == "check":
        code = run_check(out, err, param, opts)
    elif cmd == "names":
        if param == ["@"]:
            param = [
                "../../names/gather/us/names-by-year.csv",
                "../../results/whash-en.txt",
            ]
        if len(param) != 2:
            return None
        code = run_names(out, err, param, opts)
    return code

def run_check(out, err, param:list, opts:dict) -> int:
    """ Check whash files!
    """
    code = 0
    verbose = opts["verbose"]
    names = param if param else [None]
    for fname in names:
        input_name = fname if fname else "(stdin)"
        is_ok = whash_checker(out, fname if fname else "", input_name, verbose)
        if not is_ok:
            code = 1
            err.write(f"Failed 'whash' check: {input_name}\n")
    return code

def whash_checker(out, whash_fname:str, name_info:str, verbose:int=0) -> bool:
    """ Checks whash (word hash text-file).
    Returns True if all ok.
    """
    #wht = pwenvelop.whashr.Words("en"); is_ok = wht.reader("../../results/whash-en.txt")
    wht = pwenvelop.whashr.Words("*")
    if whash_fname:
        is_ok = wht.reader(whash_fname)
    else:
        is_ok = wht.reader(stream=sys.stdin)
    nick = wht.language_nick()
    hints = f"language_nick()={nick}; "
    print(f"{name_info}: ok? {is_ok}; {hints}#words: {len(wht.words)}")
    if not is_ok:
        if verbose > 0:
            print(f"whashr last_error(): {wht.last_error()}")
        return False
    for word, hsh_str in wht.words:
        hsh = int(hsh_str)
        calc = wordhash.word_hash(word)
        if hsh == calc:
            if verbose > 0:
                print(f"{hsh}\t{word}")
            continue
        if out:
            out.write(f"Mismatch ({nick}): there={hsh}, calculated={calc}\n")
        return False
    return True


def run_names(out, err, param:list, opts) -> int:
    """ Various tests on 'names-by-year.csv'
    """
    csv_name, whash_fname = param
    wht = pwenvelop.whashr.Words("*")
    is_ok = wht.reader(whash_fname)
    if not is_ok:
        return 3
    jby = yearlynames.ByYear(csv_name, "names-by-year")
    jby.reader()
    infos = {
        "nby": (jby, jby.popular()),
        "wht": (wht, wht.words),
    }
    code = names_misc(out, err, infos)
    return code

def names_misc(out, err, infos) -> int:
    pop, words = infos["nby"][1], infos["wht"][1]
    raw_year_list = [dash.split("-")[0] for dash in sorted(pop)]
    ylist = list()
    named = {
        'm': dict(),
        'f': dict(),
        'usage': dict(),
    }
    bysize = {
        3: dict(),
        4: dict(),
        5: dict(),
    }
    wide = dict()
    for s_year in sorted(set(raw_year_list)):
        male_list = pop[s_year + "-m"]
        female_list = pop[s_year + "-f"]
        amin = min(len(male_list), len(female_list))
        dprint(
            'misc',
            "s_year:", s_year,
            len(male_list), len(female_list),
            amin,
        )
        data1 = [(trip[0], percentage(trip[2])) for trip in male_list[:amin]]
        data2 = [(trip[0], percentage(trip[2])) for trip in female_list[:amin]]
        ylist.append((s_year, amin, data1, data2))
        for name, ratio in data1:
            new_ratio(name, ratio, named['m'], 'm', named['usage'])
        for name, ratio in data2:
            new_ratio(name, ratio, named['f'], 'f', named['usage'])
    if awful_debug():
        for tup in ylist:
            print(tup)
            print()
    for genre in ('m', 'f'):
        dprint('ratio', "# Genre:", genre, "; most popular:")
        for name, ratio in babies.maths.descending_ratio(named[genre]):
            dprint('ratio', f"{genre}:", name, ratio)
            if len(name) in bysize:
                bysize[len(name)][name] = ratio
    assert words
    mix_words(words, bysize, named)
    return 0

def mix_words(words, bysize:dict, named:dict):
    assert words
    for size in sorted(bysize):
        there = bysize[size]
        for name in sorted(there):
            shown = there[name]
            print("#:", size, name, shown)
    for word, genres in named['usage'].items():
        if len(genres) > 1:
            dprint('mix', "!", genres, word)

def percentage(astr:str) -> float:
    num = babies.maths.from_permil(astr)
    assert num >= 0 and num <= 1
    return num

def new_ratio(name, ratio, adict, genre, usage:dict) -> bool:
    """ Returns True if name is re-used from boys/ girls.
    """
    if babies.preclude.precluded_name(name):
        return False
    if name in adict:
        adict[name] = (adict[name] + ratio) / 2.0
    else:
        adict[name] = ratio
    if name in usage:
        usage[name] = sorted(list(set(usage[name] + [genre])))
    else:
        usage[name] = [genre]
    return len(usage[name]) > 1

def awful_debug() -> bool:
    # pwenvelop.adebug.has_debug()
    return FULL_DEBUG > 0

# Main script
if __name__ == "__main__":
    main()
