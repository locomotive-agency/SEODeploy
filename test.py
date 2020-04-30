import multiprocessing as mp
import numpy as np

def _map(args):
    lst, fn, kwa = args
    return [fn(i) for i in lst]

def mp_parse(lst, fn, **kwargs):
    threads = 5
    pool = mp.Pool(processes=threads)

    result = pool.map(_map, [(l, fn, kwargs)
            for l in np.array_split(lst, threads)])
    pool.close()

    return np.concatenate(list(result))

def square(x):
    return round(x+1)

def main():
    paths = [i for i in range(1000)]
    result = mp_parse(paths, square)
    print(len(result))
    print(paths[:10])
    print(result[:10])


if __name__ == "__main__":
    main()
