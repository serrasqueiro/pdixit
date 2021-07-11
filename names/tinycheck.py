#!/usr/bin/python3
#-*- coding: utf-8 -*-
# tinycheck.py  (c)2021  Henrique Moreira

"""
Pre-checks existing data
"""

# pylint: disable=missing-docstring

import sys
import json
import tabular.csv

CSV_ENCODING = "ISO-8859-1"

FOUT_GATHER_1 = "gather/us/names-by-year.csv"
FOUT_GATHER_2 = "gather/us/infos.txt"

F_STATES_HASH = "using/states_hash.json"
F_BABY_BY_STATE = "data-babynames/baby-names-by-state.csv"
F_BIRTHS_BY_STATE = "data-babynames/births.csv"


def main():
    """ Main function """
    prog = __file__
    code = run(sys.stdout, sys.stderr, sys.argv[1:])
    if code < 0:
        print(f"""Usage:
  {prog}

Without args:
  - checks data consistency within ../names/ directory.
""")
    sys.exit(0 if code < 0 else code)

def run(out, err, args:list) -> int:
    """ Main run """
    assert out
    debug = 0
    if args:
        return -1
    opts = {
        'states-json': F_STATES_HASH,
        'by-state-csv': F_BABY_BY_STATE,
        'births-by-state-csv': F_BIRTHS_BY_STATE,
        '@out': default_out_dict(),
    }
    msg = checker(opts, debug)
    if msg:
        if err:
            err.write(f"Failed: {msg}\n")
    result = opts['@out']
    assert result
    outputs = (
        FOUT_GATHER_1,
        FOUT_GATHER_2,
    )
    out_gather(result, ['year-most'], outputs)
    return 0

def out_gather(infos:dict, outs:list, outputs) -> bool:
    """ Output to text csv 'outputs'.
    """
    is_ok = False
    gather_csv = outputs[0]
    text_info = outputs[1]
    yearly = infos['yearly']
    for key in outs:
        there = infos[key]
        if key in ('year-most',):
            with open(gather_csv, "w", encoding=CSV_ENCODING) as fout:
                dump_names_dict(fout, there, yearly)
            is_ok = True
    # Best-effort write infos.txt
    s_txt = """# (c)2021  Henrique Moreira; gathered by tinycheck.py"""
    s_txt += '\n'.join(infos['year-info']) + '\n'
    try:
        with open(text_info, "w") as fout:
            fout.write(s_txt)
    except FileNotFoundError:
        print("Skipped output:", text_info)
    return is_ok

def dump_names_dict(fout, adict:dict, yearly=None):
    """ Write dictionary into fout stream.
    """
    pre = " " * 4
    fout.write("{")
    g_last = ""
    for key in sorted(adict):
        for genre in sorted(adict[key], reverse=True):
            s_year = f'"{key}-{genre}"'
            fout.write(f"\n{pre}],\n" if g_last else "\n")
            fout.write(f"\n{pre}{s_year}: [")
            last = ""
            for count, name in adict[key][genre]:
                fout.write(",\n" if last else "\n")
                if yearly:
                    total = yearly[genre][key]
                    shown = f'"{count}", "{nicer_percent(count, total)}"'
                else:
                    shown = f'"{count}", "-"'
                name = f'"{name}"'
                fout.write(f"{pre}{pre}[{name}, {shown}]")
                last = "y"
            g_last = "y"
    fout.write(f"\n{pre}]" if g_last else "")
    fout.write("\n}\n")

def checker(opts:dict, debug:int=0) -> str:
    """ Checks data/ file consistency.
    Filenames (and paths) are hard-coded -- it is intended to be simple.
    """
    jfname = opts['states-json']
    adict = json.load(open(jfname, "r"))
    assert isinstance(adict, dict), f"Expected to be a dictionary, but got: {type(adict)}"
    states = adict
    csv_name = opts['by-state-csv']
    if debug > 0:
        print("Reading by-state-csv:", csv_name)
    stt = tabular.csv.CSV(csv_name)
    csv_name = opts['births-by-state-csv']
    if debug > 0:
        print("Reading births-by-state-csv:", csv_name)
    births = tabular.csv.CSV(csv_name)
    yearly = calculate_yearly(births)
    aout = opts['@out']
    dbd = [states, aout]
    inputs = (
        stt,
        births,
        yearly,
    )
    tidy_by_state(inputs, states, dbd)
    by_year = aout['by-year']
    most = aout['year-most']
    totals = dict()
    years = sorted(yearly['m'])
    assert len(years) == len(yearly['f'])
    for year in years:
        totals[year] = yearly['m'][year] + yearly['f'][year]
    # Check percentage is not above 1.0 !
    aout['year-info'] = stats_year_info(by_year, yearly, totals)
    for year in years:
        # by_year[2005]['m:Henry'] = ['Henry', 'm', 1957]	(referred to as trip)
        most[year] = dict()
        for genre in yearly:
            these = by_year[year]
            vaga = [(trip[2], trip[0]) for name, trip in these.items() if trip[1] == genre]
            alist = sorted(vaga, reverse=True)
            most[year][genre] = alist
    # Update info:
    aout['yearly'] = yearly
    return ""

def tidy_by_state(inputs:tuple, states, dbd) -> str:
    stt, births, yearly = inputs
    assert births
    assert yearly
    by_year = dict()
    for idx, tup in stt.rows:
        assert idx > 0
        abbrev, year, name, count, boy = tup
        if name == "\xa0" or count in ("NA",):
            continue
        if abbrev not in states:
            return f"Invalid state abbreviation, line {idx}: '{abbrev}'"
        if boy in ("boy", "girl"):
            boy = boy == "boy"
        else:
            return f"Invalid genre, line {idx}: {tup}"
        genre = "m" if boy else "f"
        year = int(year)
        count = int(count)
        data = [name, genre, count]
        if year not in by_year:
            by_year[year] = dict()
        key = f"{genre}:{name}"
        if key in by_year[year]:
            by_year[year][key][2] += count
        else:
            by_year[year][key] = data
    if dbd:
        dbd[1]['by-year'] = by_year
    return ""

def calculate_yearly(births) -> dict:
    """ Births is a CSV class
    births.rows[0] = [2, ['1981', 'AK', 'boy', '4721']]
    """
    # pylint: disable=line-too-long
    yearly = {
        'm': dict(),
        'f': dict(),
    }
    births.tidy()
    is_ok = ';'.join(births.column_names()) == 'year;state;sex;births'
    assert is_ok
    for genre in ('m', 'f'):
        for year in range(1970, 2050+1):
            sex = "boy" if genre == 'm' else "girl"
            counts = [int(tup[3]) for _, tup in births.rows if tup[2] == sex and int(tup[0]) == year]
            if not counts:	# List is empty
                continue
            total = sum(counts)
            yearly[genre][year] = total
    return yearly

def stats_year_info(by_year, yearly, totals) -> list:
    result = list()
    for year in totals:
        parts = [by_year[year][item][2] for item in by_year[year]]
        count = sum(parts)
        is_ok = count <= totals[year]
        assert is_ok, f"Bogus year {year}, totals={totals[year]}, but count={count}"
        for genre in yearly:
            there = yearly[genre][year]
            assert there > 0
            parts = [triple[2] for _, triple in by_year[year].items() if triple[1] == genre]
            count = sum(parts)
            is_ok = count <= there
            assert is_ok, f"Bogus year for genre={genre}, there={there}, count={there}"
            perc = round((there-count) * 100.0 / there, 0)
            s_info = f"{year}.{genre}: {perc:02.0f}% {count} of {there}"
            result.append(s_info)
    return result

def nicer_percent(num:int, denom:int, invalid="-1.0", perm=True) -> str:
    if denom == 0:
        return invalid
    sub = round(num * 100.0 / float(denom), 2)
    if perm and sub <= 0.0:
        sub = round(num * 1000.0 / float(denom), 2)
        if sub <= 0.0:
            return "-"
        return f"{sub:.2f}%o"
    return f"{sub:.2f}%"

def json_out(table) -> str:
    alist = sorted(table, key=lambda k: k["Id"])
    content = json.dumps(alist, indent=2, sort_keys=True)
    return content

def from_yearly(yearly:dict, genre:str):
    result = list()
    adict = yearly[genre]
    an_id = 0
    for year in adict:
        an_id += 1
        item = {
            "Id": an_id,
            "genre": genre,
            "year": year,
            "count": yearly[genre][year],
        }
        result.append(item)
    # Usage example:
    #	astr = json_out(from_yearly(yearly, 'm'))
    return result

def default_out_dict() -> dict:
    adict = {
        'by-year': dict(),
        'year-most': dict(),
        'year-info': list(),
        'yearly': dict(),
    }
    return adict

if __name__=="__main__":
    main()
