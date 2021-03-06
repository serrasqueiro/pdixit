#-*- coding: utf-8 -*-
# pwordhash.py  (c)2021  Henrique Moreira

"""
Dumps words hashes
"""

# pylint: disable=unused-argument

import sys
import os.path
import pwh.wordhash as wordhash
import pwh.wordhashf as wordhashf
import pwh.leandir as leandir
import pwh.wexcept as wexcept

DEBUG = 0
RES_JSON_FILES = (
    "exceptions.json",
)

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
    first = ""
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
    if param:
        first = param[0]
    else:
        param = [wordhash.DEFAULT_TWO_LETTER_LANG]
    if os.path.isdir(first):
        params = param[1:]
        if params:
            return None
        return dump_dir(out, err, first, params, opts, debug)
    for name in param:
        nick = name
        # if nick is a two-letter, use e.g. ../../results/strict-pt.lst
        if wordhash.valid_nick(nick):
            fname = os.path.join("..", "..", "results", f"strict-{nick}.lst")
        else:
            fname = name
            nick = wordhash.nick_from_name(name)
        dump_nick(out, err, nick, fname, opts, debug)
    return 0

def dump_nick(out, err, nick, fname, opts, debug=0) -> int:
    """ Dumps file or nick. """
    show_data = bool(opts.get("show-data")) and out
    whash = wordhash.WordHash(nick, fname)
    wset = wordhashf.dump_wordlist(out, err, whash, opts)
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

def dump_dir(out, err, dirname:str, param:list, opts, debug=0) -> int:
    """ Dumps dir """
    #debug = 1
    assert not param, "Unexpected parameters"
    adir = leandir.DirFiles(dirname)
    json_files = [[name, adir.path_at(name), []] for name in adir.files() if name in RES_JSON_FILES]
    exc_files = [[name, adir.path_at(name), []] for name in adir.files() if name.startswith("exc-")]
    if debug > 0:
        print("Files:", adir.files())
        print("json files:", json_files)
        for triplet in adir.triplets():
            print(triplet[0], f"(at: {triplet[1]})", triplet[4:])
    wexc = wexcept.WExcept(nick="exceptions.json")
    if json_files:
        for name, path, alist in json_files:
            assert not alist
            wexc = wexcept.WExcept(path, name)
            is_ok = wexc.reader()
            if not is_ok:
                print("Bogus exceptions:", path)
                print(">>>", wexc.last_message())
                return 5
            print("Read:", name)
            wexc.simple_index("Kind")
    if debug > 0:
        print("Exceptions JSON,", wexc.jname(), ">>>", wexc.map(), "; any_ok():", wexc.any_ok())
        for an_id in sorted(wexc.map()):
            what = wexc.map()[an_id]
            kind = what['Kind']
            print(f"Exception, id={an_id} Kind={kind}, Desc='{what['Desc']}'",
                  "check id:",
                  wexc.byname(kind))
    # Check if exceptions are well-formed
    for name, path, alist in exc_files:
        excl = wordhash.from_exclusion_file(path, wexc.encoding())
        print(f">>> {name} (at {path}, exceptions size: {len(excl['why'])})")
        for key in sorted(excl["why"], key=str.casefold):
            why = excl["why"][key]
            s_why = why if why else "-"
            if not wexc.any_ok():
                if debug > 0:
                    print("?", key, s_why)
                continue
            an_id = wexc.byname(why)
            if debug > 0:
                print("!", key, s_why, an_id)
            if an_id < 0:
                err.write(f"{name}: Unknown exception kind for '{s_why}'\n")
    if not exc_files:
        err.write(f"No files at: {dirname}\n")
        return 2
    if not json_files:
        err.write(f"No exceptions.json at: {dirname}\n")
    exc_files_list = [name for name, _, _ in exc_files]
    show_langs(out, err, adir, exc_files_list, opts)
    return 0

def show_langs(out, err, adir, exc_files_list, opts):
    """ Show 'strict-??.lst' """
    show_data = bool(opts.get("show-data"))
    for name in adir.files():
        path = adir.path_at(name)
        if not name.endswith(".lst"):
            continue
        if name in exc_files_list:
            continue
        nick = wordhash.nick_from_name(name)
        print(f"# strict-name: {name}, path={path}; nick={nick}")
        assert nick
        alist = one_lang_list(path, nick, opts, err)
        if not show_data:
            print("Word-lines: {len(alist)}")
            continue
        assert alist
        for line in alist:
            shown = line + "\n"
            out.write(shown)

def one_lang_list(path, nick, opts, err=None) -> list:
    """ Returns one language word-hash a list of strings. """
    whash = wordhash.WordHash(nick, path)
    wset = wordhashf.dump_wordlist(None, err, whash, opts)
    alist = wordhashf.wset_words(wset, err)
    return alist

# Main script
if __name__ == "__main__":
    main()
