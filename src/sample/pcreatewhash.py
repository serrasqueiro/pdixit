#-*- coding: utf-8 -*-
# pcreatewhash.py  (c)2021  Henrique Moreira

"""
Create Word hashes from .lst file(s)
"""

# pylint: disable=unused-argument

import sys
import os.path
from xywinter.typeproxy import DictProxy
import pwh.wordhash as wordhash
import pwh.wordhashf as wordhashf

DEBUG = 0

def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""pcreatewhash.py [options] path-lst

Options are:
   -v      Verbose
""")
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    debug = DEBUG
    param = args
    opts = {
        "verbose": 0,
        "show-all": True,
        "show-data": False,
        "force": False,
        }
    while param and param[0].startswith('-'):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            opts["show-data"] = True
            opts["verbose"] += 1
            continue
        if param[0] in ("-f",):
            opts["force"] = True
            del param[0]
            continue
        return None
    if not param:
        return None
    path = param[0]
    del param[0]
    if param:
        return None
    code, alash = reader(out, err, path, opts, debug)
    if code:
        err.write(f"Error-code {code}, handling: {path}\n")
    else:
        code = writer(out, err, (path, path + ".txt"), alash, opts, debug)
    return code

def writer(out, err, paths, alash:dict, opts, debug=0):
    """ Write output language """
    force_out = opts["force"]
    _, indicative_name = paths
    lang = alash["lang"]
    if not lang:
        lang = "unknown"
    if not lang.isalpha():
        return 3 # Invalid language (string)
    out_fname = os.path.join(os.path.dirname(indicative_name), f"whash-{lang}.txt")
    if opts["verbose"] > 0:
        print("# Output to:", out_fname)
    if not force_out and os.path.isfile(out_fname):
        err.write(f"Cowardly refusing to overwrite: {out_fname}\n")
        return 4
    with open(out_fname, "wb") as fout:
        s_all = whash_writer(alash)
        fout.write(s_all.encode("ascii"))
    return 0

def whash_writer(alash) -> str:
    """ Language hash writer. """
    result = ""
    wthere = alash["word-to-hash"]
    words = sorted(wthere, key=str.casefold)
    for word in words:
        hsh = wthere[word]
        shown = f"{word} {hsh}\n"
        result += shown
    return result

def reader(out, err, path, opts, debug=0) -> tuple:
    """
    :param out: output stream (may be None)
    :param err: error stream
    :param path: full path of .lst file
    :param opts: options
    :param debug: debug > 0 for showing debug
    :return: error-code, and the 'alash'
    """
    fname = path
    nick = wordhash.nick_from_name(fname)
    alash = lang_hash_create(nick, fname, opts, err)
    alist = alash["hashes"]
    wset = alash["wset"]
    if debug > 0:
        debug_dump_wset(wset)
    if not alist:
        return 3, dict()
    show_data = bool(opts.get("show-data")) and out
    if show_data:
        for line in alist:
            out.write(line + "\n")
    return 0, alash

def debug_dump_wset(wset:dict):
    """ Debug: dump 'wset', a (word-hash) dictionary """
    dproxy = DictProxy(wset)
    desc = dproxy.resume2()
    for tup in desc:
        name, typeinfo, num = tup
        print("#", name, typeinfo, num)
    print("---")

def lang_hash_create(nick, fname, opts, err) -> dict:
    """ Language hash create. """
    whash = wordhash.WordHash(nick, fname)
    wset = wordhashf.dump_wordlist(None, err, whash, opts)
    queue = wset["queue"]
    if queue:
        alist = wordhashf.wset_words(wset, err)
    else:
        alist = list()
        err.write(f"lang_hash_create() for '{nick}', failed: {fname}\n")
    adict = {
        "lang": nick,
        "path": fname,
        "hashes": alist,
        "wset": wset,
        "word-to-hash": wset['wthere'],
    }
    return adict

# Main script
if __name__ == "__main__":
    main()
