#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with it. If not, see <http://www.gnu.org/licenses/>.


import itertools
import unicodedata

def write_string_to_file(string, filename):
  f = open(filename, "w")
  f.write(string)
  f.close()

def write_stream_to_file(stream, filename):
    CHUNK = 16 * 1024
    output = open(filename, "wb")
    while True:
        chunk = stream.read(CHUNK)
        if not chunk: break
        output.write(chunk)
    stream.close()
    output.close()

def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
       and whose values are a set of dependent items. Output is a list of
       sets in topological order. The first set consists of items with no
       dependences, each subsequent set consists of items that depend upon
       items in the preceeding sets.

       >>> print '\\n'.join(repr(sorted(x)) for x in toposort2({
       ...     2: set([11]),
       ...     9: set([11,8]),
       ...     10: set([11,3]),
       ...     11: set([7,5]),
       ...     8: set([7,3]),
       ...     }) )
       [3, 5, 7]
       [8, 11]
       [2, 9, 10]
    """
    def toposort2(data):
        from functools import reduce
        # Ignore self dependencies.
        for k, v in data.items():
            v.discard(k)
        # Find all items that don't depend on anything.
        extra_items_in_deps = reduce(set.union, data.itervalues()) - set(data.iterkeys())
        # Add empty dependences where needed
        data.update({item:set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.iteritems() if not dep)
            if not ordered:
                break
            yield ordered
            data = {item: (dep - ordered)
                    for item, dep in data.iteritems()
                        if item not in ordered}
        assert not data, "Cyclic dependencies exist among these items:\n%s" % '\n'.join(repr(x) for x in data.iteritems())
    return itertools.chain.from_iterable(toposort2(data))

def to_ascii(utf):
    return unicodedata.normalize('NFD',unicode(utf)).encode("ascii","ignore")


