#-*- coding: utf-8 -*-
# leandir.py  (c)2021  Henrique Moreira

"""
Classes for Files in Dirs (Unix style always)
"""

# pylint: disable=unused-argument

import os
import stat
import pwh.luxperm as luxperm

class LDir():
    """ Unix path (or Windows folder) """
    _path = ""

    @staticmethod
    def strip_dir(name:str) -> str:
        """ Simplified string name (to Unix) """
        guard = 1000
        astr = name.replace("\\", "/")
        while "//" in astr:
            astr = astr.replace("//", "/")
            guard -= 1
            assert guard >= 0
        if len(astr) > 1 and astr.endswith("/"):
            astr = astr[:-1]
        return astr.strip()

    @staticmethod
    def is_file(astat) -> bool:
        """ Returns True if astat st_mode is a file """
        if isinstance(astat, str):
            return os.path.isfile(astat)
        return stat.S_ISREG(astat.st_mode)

    @staticmethod
    def is_dir(astat) -> bool:
        """ Returns True if astat st_mode is a file """
        if isinstance(astat, str):
            return os.path.isfile(astat)
        return stat.S_ISDIR(astat.st_mode)

class DirFiles(LDir):
    """ List of files """
    _files = None
    _dirs = None
    _trips = None
    _map = None

    def __init__(self, apath="", scan_dir=True):
        """ Class initializer """
        self._path = LDir.strip_dir(apath)
        self._files, self._dirs = list(), list()
        self._trips = list()
        self._map = dict()
        if scan_dir:
            self.scan_dir()

    def files(self) -> list:
        """ Returns file names """
        return self._files

    def triplets(self) -> list:
        """ Returns list of triplets """
        return self._trips

    def path_at(self, name:str) -> str:
        """ Returns the entire path for the entered name """
        return self._map[name][0]

    def scan_dir(self) -> bool:
        """ Scan directory """
        apath = self._path
        alist = list()
        dirs = list()
        trips = [(elem.name, apath + "/" + elem.name, elem, elem.stat()) for elem in
                 os.scandir(apath)]
        where = dict()
        for name, path, elem, astat in trips:
            where[name] = (path, elem, astat)
            is_file = LDir.is_file(astat)
            if is_file:
                alist.append(name)
            elif LDir.is_dir(astat):
                dirs.append(name)
        trips = list()
        self._files = sorted(alist, key=str.casefold)
        self._dirs = sorted(dirs, key=str.casefold)
        for name in self._dirs:
            ux_perm = "d" + luxperm.permissions_to_unix_string(where[name][2].st_mode)
            trips.append([name] + list(where[name]) + [ux_perm])
        for name in self._files:
            ux_perm = "-" + luxperm.permissions_to_unix_string(where[name][2].st_mode)
            trips.append([name] + list(where[name]) + [ux_perm])
        self._trips = trips
        self._map = where
        return True

# Main script
if __name__ == "__main__":
    print("Please import me.")
