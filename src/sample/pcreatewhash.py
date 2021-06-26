#-*- coding: utf-8 -*-
# pcreatewhash.py  (c)2021  Henrique Moreira

"""
Create Word hashes from .lst file(s)
"""

# pylint: disable=unused-argument

import sys
import os.path
from waxpage.redit import char_map
import pwh.wordhash as wordhash
import pwh.leandir as leandir
import pwh.wexcept as wexcept
import pwordhash

DEBUG = 0
RES_JSON_FILES = (
    "exceptions.json",
)

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
        return None
    path = param[0]
    del param[0]
    if param:
        return None
    code = reader(out, err, path, opts, debug)
    if code:
        err.write(f"Error-code {code}: handling {path}\n")
    return 0

def reader(out, err, path, opts, debug=0) -> int:
    fname = path
    nick = wordhash.nick_from_name(fname)
    alash = lang_hash_create(out, err, nick, fname, opts, debug)
    alist = alash["hashes"]
    show_data = bool(opts.get("show-data")) and out
    if show_data:
        for line in alist:
            out.write(line + "\n")
    return 0

def lang_hash_create(out, err, nick, fname, opts, debug=0) -> dict:
    """ Language hash create. """
    whash = wordhash.WordHash(nick, fname)
    wset = pwordhash.dump_wordlist(None, err, whash, opts)
    alist = pwordhash.wset_words(wset, err)
    adict = {
        "lang": nick,
        "path": fname,
        "hashes": alist,
    }
    return adict

# Main script
if __name__ == "__main__":
    main()
