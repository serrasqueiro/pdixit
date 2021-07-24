#-*- coding: utf-8 -*-
# coder.py  (c)2021  Henrique Moreira

"""
Dump to text (using 'whash').
"""

# pylint: disable=missing-function-docstring

import sys
import pwenvelop.whashr
import dtable.textdict

def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""coder.py COMMAND [options] [file(s)]

Commands are:
   tabled     Dump table using whash-en-ascii.txt or other whash files.
              Syntax: tabled whash-file input-file [input-file ...]

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
    if cmd == "tabled":
        whashes = [
            "../../results/whash-en-ascii.txt",
        ]
        if not param:
            return None
        if param[0]:
            if param[0] != "@":
                whashes = [param[0]]
            inputs = param[1:]
        else:
            inputs = []
        code = run_tabled(out, err, whashes, inputs, opts)
    return code

def run_tabled(out, err, whashes:list, inputs:list, opts:dict) -> int:
    """ Check whash files!
    """
    code = 0
    key_sep = "\t"
    assert whashes
    assert len(whashes) == 1
    verbose = opts["verbose"]
    names = inputs if inputs else [None]
    whash_fname = whashes[0]
    wht = pwenvelop.whashr.WordsA("*")
    is_ok = wht.reader(whash_fname)
    if not is_ok:
        err.write(f"Failed read: {whash_fname}\n")
        return 1
    d_ascii = wht.get_extra_dict()
    if not d_ascii:
        err.write(f"Not found ASCII for: {whash_fname}\n")
        return 2
    for fname in names:
        hint = f" (using {whash_fname})" if verbose else ""
        if fname is None:
            data = sys.stdin.read()
        else:
            err.write(f"Processing input{hint}: {fname}\n")
            data = open(fname, "r").read()
        tdt = dtable.textdict.TextDict()
        tdt.processor(data)
        is_ok = tdt.to_dict()
        if not tdt.get_dict():
            return 3
        for key, text in tdt.get_by_ids():
            words  = to_word(text, d_ascii)
            shown = ', '.join(words)
            astr = f"{key}{key_sep}{shown}\n"
            out.write(astr)
    return code

def to_word(astr:str, d_ascii:dict) -> tuple:
    result = list()
    for achr in astr:
        new = d_ascii[ord(achr)]
        # Choose one arbitrary word (the first)
        word = new[0]
        result.append(word)
    return tuple(result)

# Main script
if __name__ == "__main__":
    main()
