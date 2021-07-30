#-*- coding: utf-8 -*-
# pin_conv.py  (c)2021  Henrique Moreira

"""
Simple converter of 3 to 7 digit pins.
"""

# pylint: disable=unused-argument

import sys
import pwenvelop.whashr

def main():
    """ Main script.
    """
    code = run_main(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print("""pin_conv.py [options] whash-input-text pin [pin ...]
""")
    sys.exit(code if code else 0)


def run_main(out, err, args):
    """ Main run.
    """
    if len(args) < 2:
        return None
    # whash_fname = "results/whash-pt.txt"
    param = args
    whash_fname, rest = param[0], param[1:]
    wht = pwenvelop.whashr.Words("*")
    wht.reader(whash_fname)
    is_ok = wht.hash_by_num()
    if not is_ok:
        err.write(f"No complete hash: {whash_fname}\n")
        return 1
    for item in rest:
        if not item.isdigit():
            return 3
        value = int(item)
        assert value >= 0
        if len(item) > 7:
            err.write(f"Invalid PIN: {item}\n")
            return 4
    code = go_pins(out, wht, rest)
    return code

def go_pins(out, wht, pins:list) -> int:
    """ Outputs the pin, semi-blurred.
    """
    for pin in pins:
        astr = pin_string(pin, wht)
        assert astr
        out.write(f"{astr}\n")
    return 0

def pin_string(pin:str, wht) -> str:
    """ Returns the corresponding PIN semi-blurred string! """
    value = int(pin)
    assert value >= 0
    if len(pin) <= 3:
        words = wht.by_num(value)
        return words[0]
    if len(pin) in (5, 6):
        left = pin_string(pin[:3], wht)
        right = pin_string(pin[3:], wht)
    elif len(pin) == 4:
        left = pin[0]
        right = pin_string(pin[1:], wht)
    elif len(pin) == 7:
        left = pin[0]
        right = pin_string(pin[1:], wht)
    return '.'.join([left, right])

# Main script
if __name__ == "__main__":
    main()
