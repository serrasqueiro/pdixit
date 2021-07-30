#-*- coding: utf-8 -*-
# whash_ascii.py  (c)2021  Henrique Moreira

"""
Dumps words hashes, with ASCII symbols
"""

# pylint: disable=unused-argument

import sys
import os.path
import pwh.wordhash as wordhash
from pwenvelop.whashr import WHASH_ENCODING

def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""whash-ascii.py [options] whash-input-text

Options are:
   -v      Verbose
""")
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    whash_base = "whash-" + wordhash.DEFAULT_TWO_LETTER_LANG + ".txt"
    param = args
    opts = {
        "verbose": 0,
        }
    while param and param[0].startswith('-'):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            opts["verbose"] += 1
            continue
        return None
    if not param:
        param = [os.path.join("..", "..", "results", whash_base)]
    for fname in param:
        code = go_gen_text(fname, os.path.dirname(fname), opts)
        if code:
            return code
    return 0

def go_gen_text(fname:str, outdir:str, opts) -> int:
    """ Generates a derivate file that contains the same text, but with hints for ASCII nums.
    """
    verbose = opts["verbose"]
    enc = WHASH_ENCODING
    lines = open(fname, "r", encoding=enc).readlines()
    if not lines:
        return 2
    base = ".".join(os.path.basename(fname).split(".")[:-1])
    outname = os.path.join(outdir, base + "-ascii.txt")
    if verbose > 0:
        print(f"Input: '{fname}', Output: '{outname}'")
    assert not base.endswith(("-", "."))
    return writer(outname, lines, enc)

def writer(outname:str, lines:list, enc:str) -> int:
    """ Write output file 'outname' (text-file) """
    mapa = dict()
    items = list()
    for line in lines:
        line = line.rstrip()
        if line.startswith("#"):
            items.append(f"{line}\n")
            continue
        word, anum = line.split(" ", maxsplit=1)
        num = int(anum)
        if ' ' <= chr(num) <= '~':
            what = show_ascii(num)
            if num in mapa:
                mapa[num].append(word)
                mapa[num].sort()
            else:
                mapa[num] = [word]
        else:
            what = ""
        post = f" {what}" if what else ""
        items.append(f"{line}{post}\n")
    with open(outname, "w", encoding=enc) as fout:
        fout.write(''.join(items))
        fout.write("# ASCII\n")
        for num in sorted(mapa):
            what = show_ascii(num)
            shown = '; '.join(mapa[num])
            fout.write(f"{num:03}d {what} {shown}\n")
    return 0

def show_ascii(num:int) -> str:
    """ Returns a readable string to exhibit the ASCII 'num'.
    """
    achr = chr(num)
    desc = {
        " ": 'blank',
        "'": 'quote',
        ",": 'comma',
        "`": 'back-quote',
        "\\": 'backslash',
        "(": 'open-parenthisis',
        ")": 'close-parenthisis',
        "_": 'underscore',
        "|": 'pipe',
    }
    if achr in desc:
        return "(" + desc[achr] + ")"
    return f"{achr}"

# Main script
if __name__ == "__main__":
    main()
