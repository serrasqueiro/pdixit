#-*- coding: utf-8 -*-
# wexcept.py  (c)2021  Henrique Moreira

"""
Classes for Word exceptions (including JSON handling)
"""

# pylint: disable=unused-argument

import json
import pwh.idjson as idjson

class WExcept(idjson.GenIds):
    """ Word Exceptions """
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
            alist = json.loads(open(path, "r", encoding=self._encoding).read())
        else:
            alist = list()
        msg = self._parse(alist)
        self._msg = msg
        return msg == ""

    def _parse(self, alist) -> str:
        """ Returns empty on success, or the error string if there is a problem. """
        msg = self.add_ids(alist)
        return msg

# Main script
if __name__ == "__main__":
    print("Please import me.")
