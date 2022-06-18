# pdixit -- Python Dixit

'Ipse dixit' ! (see [wikipedia](https://en.wikipedia.org/wiki/Ipse_dixit)), "he said himself"
- (a dogmatic expression in latin).
[pdixit](https://github.com/serrasqueiro/pdixit/) is a public package containing multiple language dictionaries, for the purpose of _simple codings_.

* TOC

  + [Installation](#Installation)
    ++ [openSUSE](#openSUSE)
  + [Starting dixit](#starting-dixit)

* * *

# Installation

You need Python3, and preferably a Linux running system with 'aspell' installed.
It is platform independent, but in the following examples we are assuming you use _openSUSE_.
- see also [opensuse.org/](https://www.opensuse.org/)

## openSUSE
Install the basic 'aspell' package dictionaries, the very basic one is 'english':
```
sudo zypper install -y aspell-en
```

If you like additional languages, for instance, standard portuguese and french:
```
sudo zypper install -y aspell-pt_PT aspell-fr
```

pdixit has a hard-coded dictionary with words that are not eligible for _simple codings_;
the reason to not make them eligible is explicit.
```
aah@interj
aha@interj
shit@interj
tbs@abbrev
tbsp@abbrev
tnpk@abbrev
yup@interj
```
These are just examples.

## Starting _dixit_

- The set of files within `results/` are sourced from the _**aspell**_ dictionaries.
The complete flow is explained later (see section _**Building dixit**_).

- First, run the script `./generate.sh start`
- or `./generate.sh start lang1 lang2 ...` to specify the languages you want to support.

_start_ stands for ...start using. It does not install aspell.

> Hint:
> - if you use `./generate.sh show` you will see the languages supported by your Linux/ OS.

## Building _dixit_

~~~~
Tbd.
~~~~

## Creating _whash_ (word-hashing text-file)
1. Either you use dictraw/strict-en.lst, created (by this script _start_ command), or you use what is already at _results_ folder.
1. `cd src/sample/`
1. `python pcreatewhash.py ../../results/strict-en.lst`
   + output will be at: ../../results/whash-en.txt

# Names sub-project

We have included a couple of sub-modules that handle _baby names_, specifically to allow expanding a pass dictionary with short (simple) first names of persons.

To get the latest stuff, do:
- `git submodule update --init --recursive names/data-babynames`
- `git submodule foreach "(git checkout master; git pull)"`


`--`

> _*dixit*_ -- The End

