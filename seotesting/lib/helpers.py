
#! /usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2020 JR Oakes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Interable grouping function
def group_batcher(iterator, result, count, fill=0):

    """Pings ContentKing with Paths across both staging and production websites.

    Parameters
    ----------
    iterator: list or tuple
        Iterable object
    result: type
        How the results should be returned
    count: int
        How many in each Group
    fill: str, int, float, or None
        Fill overflow with this value. If None, no fill is performed.

    """

    itr = iter(iterator)
    grps = -(-len(iterator)//count)
    for i in range(grps):
        num = len(iterator) % count if fill is None and grps-i == 1 else count
        yield result([next(itr, fill) for i in range(num)])




# Multiprocessing functions
def _map(a):
    lst, fn, args = a
    return fn(lst, **args)


def mp_list_map(lst, fn, **args):

    threads = config.THREADS
    pool = mp.Pool(processes=threads)

    result = pool.map(_map, [(l, fn, args)
            for l in np.array_split(lst, threads)])

    pool.close()

    return list(np.concatenate(result))
