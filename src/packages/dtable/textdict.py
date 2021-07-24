#-*- coding: utf-8 -*-
# textdict.py  (c)2021  Henrique Moreira

"""
Tests text Classes for handling text-files as dictionaries.
"""

# pylint: disable=missing-function-docstring

import json

DEFAULT_ENCODING = "ISO-8859-1"


class GenText():
    """ Generic Text abstract class. """
    _msg = ""
    _path = ""
    _encoding = DEFAULT_ENCODING

    def __init__(self, path="", encoding="ascii"):
        """ Class initializer """
        self._msg = ""
        self._path = path
        self._encoding = encoding if encoding else DEFAULT_ENCODING

    def last_error(self):
        """ Returns the string of last error. (And cleans up var.)
        """
        astr = self._msg
        self._msg = ""
        return astr

    def io_encoding(self):
        """ Returns the input/ output encoding.
        """
        return self._encoding

    def loader(self) -> dict:
        """ Returns the object (list or dict).
        'json.loads' verifies the syntax itself, or fails with a miserable exception.
        """
        path = self._path
        if not path:
            return list()
        an_obj = json.loads(open(path, "r", encoding=self._encoding).read())
        return an_obj

    @staticmethod
    def _parse_lines(lines) -> tuple:
        headers, payload = list(), list()
        for line in lines:
            if line.startswith("#"):
                headers.append(line[1:].strip())
            else:
                payload.append(line)
        return (headers, payload)


class TextDict(GenText):
    """ Load text, semi-colon separated, and build the appropriate dictionary.
    """
    _content = None
    _liner = None
    _ids = None

    def __init__(self, path="", column_separator=";", encoding=""):
        """ Class initializer """
        super().__init__(path, encoding)
        self._col_separator = column_separator
        self._content = {'header': "", 'payload': dict()}
        self._liner = dict()
        self._ids = list()

    def header(self) -> str:
        return self._content['header']

    def payload(self) -> dict:
        return self._content['payload']

    def reader(self) -> bool:
        """ Returns True if read succeeded.
        """
        path = self._path
        if not path:
            return False
        try:
            data = open(path, "r", encoding=self._encoding).read()
        except UnicodeDecodeError as msg:
            self._msg = msg
            return False
        assert "\r" not in data, f"CR found: '{path}'"
        lines = data.splitlines(False)
        headers, payload = GenText._parse_lines(lines)
        header = headers[0] if headers else ""
        self._content['header'], self._content['payload'] = header, payload
        return True

    def get_dict(self) -> dict:
        """ Returns the dictionary built from the lines (default dictionary.)
        """
        return self._liner

    def to_dict(self, lead_keys=1) -> bool:
        """ Returns True if content (line-by-line) could get put into a dictionary.
        """
        assert lead_keys >= 0, f"lead_keys should be a non-negative number, got: {lead_keys}"
        self._ids = list()
        col_sep = self._col_separator
        liner = dict()
        idx = 0
        for line in self._content['payload']:
            idx += 1
            if col_sep:
                spl = line.split(col_sep, maxsplit=lead_keys)
            else:
                spl = [line]
            if lead_keys:
                key, there = spl[0], spl[1:]
            else:
                key, there = line, None
            if key in liner:
                self._msg = f"Duplicate key: '{key}' (idx={idx})"
                return False
            if there is None:
                liner[key] = idx
                continue
            liner[key] = there
            json_text = col_sep.join(there)
            cell = {"Id": idx, "Key": key, "Text": json_text}
            self._ids.append(cell)
        self._liner = liner
        return True

    def json_string(self) -> str:
        return json_writer_by_id(self._ids)


def json_writer_by_id(adict:dict) -> str:
    """ Returns the json string for dictionary 'adict'.
    """
    content = sorted(adict, key=lambda k: k["Id"])
    astr = json.dumps(content, indent=2, sort_keys=True)
    astr += "\n"
    return astr

# Main script
if __name__ == "__main__":
    print("Please import me.")
