#-*- coding: utf-8 -*-
# idjson.py  (c)2021  Henrique Moreira

"""
Generic Classes for json/ id handling
"""

# pylint: disable=missing-function-docstring

class GenIds():
    """ Generic IDs """
    _name = ""
    _encoding = ""
    _ids = list()
    _id_map = dict()
    _simple_uniq = None
    _msg = ""

    def __init__(self, name=""):
        """ Class initializer """
        self._name = name
        self._encoding = GenIds.default_encoding()
        self._simple_uniq = None
        self.reset_ids()

    def encoding(self) -> str:
        """ Returns the encoding (string). """
        return self._encoding

    def any_ok(self) -> bool:
        """ Returns True if any _simple_uniq seems valid. """
        is_ok = self._simple_uniq is not None
        return is_ok

    @staticmethod
    def default_encoding() -> str:
        return "ISO-8859-1"

    def reset_ids(self):
        """ Reset all internal maps """
        self._msg = ""
        self._ids, self._id_map = list(), dict()

    def jname(self) -> str:
        """ The basename of the filename (string), ending with '.json' """
        return self._name

    def last_message(self) -> str:
        """ Returns the last error message (empty means ok). """
        return self._msg

    def map(self) -> dict:
        """ Returns the map which relates an 'Id' to a (Value) dictionary """
        return self._id_map

    def add_ids(self, alist:list, uniq:bool=True) -> str:
        """ Returns empty on success, or the error string if there is a problem. """
        for item in alist:
            self._ids.append(item)
            an_id = item["Id"]
            if not isinstance(an_id, int):
                return f"ID not an integer: '{an_id}'"
            adict = dict()
            for key, value in item.items():
                if key in ("Id",):
                    continue
                adict[key] = value
            if uniq:
                if an_id in self._id_map:
                    return f"Duplicate ID: '{an_id}', for: {adict}"
            self._id_map[an_id] = adict
        return ""

    def simple_index(self, field:str) -> bool:
        """ Tries to index by the field. """
        by_field = dict()
        for an_id, adict in self._id_map.items():
            by_field[adict[field]] = an_id
        self._simple_uniq = by_field
        return True

    def byname(self, name) -> int:
        assert isinstance(self._simple_uniq, dict)
        if name not in self._simple_uniq:
            return -1
        return self._simple_uniq[name]

# Main script
if __name__ == "__main__":
    print("Please import me.")
