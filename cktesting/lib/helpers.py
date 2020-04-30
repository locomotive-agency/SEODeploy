



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
