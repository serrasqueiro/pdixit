#-*- coding: utf-8 -*-
# luxperm.py  (c)2021  Henrique Moreira

"""
Unix-like functions
"""

import stat

def permissions_to_unix_string(st_mode) -> str:
    # pylint: disable=line-too-long
    """
    :param st_mode: Unix status, provided by POSIX lstat() or stat()
    :return: string

    see also https://stackoverflow.com/questions/17809386/how-to-convert-a-stat-output-to-a-unix-permissions-string/17810089
    """
    permstr = ''
    usertypes = ['USR', 'GRP', 'OTH']
    for usertype in usertypes:
        perm_types = ['R', 'W', 'X']
        for permtype in perm_types:
            perm = getattr(stat, 'S_I%s%s' % (permtype, usertype))
            if st_mode & perm:
                permstr += permtype.lower()
            else:
                permstr += '-'
    return permstr

# Main script
if __name__ == "__main__":
    print("Please import me.")
