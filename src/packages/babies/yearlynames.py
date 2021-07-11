#-*- coding: utf-8 -*-
# yearlynames.py  (c)2021  Henrique Moreira

"""
Classes for handling 'names-by-year.csv'
"""

# pylint: disable=unused-argument

import json
import pwh.idjson as idjson
import pwh.dataconv as dataconv

class ByYear(idjson.GenIds):
    """ JSON reader """
    _listing = None

    def __init__(self, path="", nick=""):
        """ Class initializer """
        super().__init__(nick)
        self._path = path

    def reader(self) -> bool:
        """ Returns True if JSON read succeeds semantically.
        Currently no syntax check is done.
        """
        path = self._path
        if path:
            an_obj = json.loads(open(path, "r", encoding=self._encoding).read())
        else:
            an_obj = dict()
        assert isinstance(an_obj, dict)
        year = int(sorted(an_obj)[0].split("-")[0])
        assert year >= 1980, f"Invalid year: '{year}'"
        alist = dataconv.to_list(an_obj, 101)
        msg = self._parse(alist)
        self._msg = msg
        return msg == ""

    def listing(self) -> list:
        """ Returns current listing.
        """
        assert self._listing is not None
        return self._listing

    def _parse(self, alist) -> str:
        """ Returns empty on success, or the error string if there is a problem. """
        msg = ""
        #msg = self.add_ids(alist)
        self._listing = alist
        return msg

# Main script
if __name__ == "__main__":
    print("Please import me.")
