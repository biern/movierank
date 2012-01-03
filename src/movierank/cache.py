import pickle
import os

CACHE_FILENAME = ".movierank-"


def load_cache(directory, suffix="cache"):
    path = os.path.join(directory, CACHE_FILENAME + suffix)
    if os.path.exists(path):
        return pickle.load(open(path))

    return None


def store_cache(directory, dbs, suffix="cache"):
    path = os.path.join(directory, CACHE_FILENAME + suffix)
    pickle.dump(dbs, open(path, 'w'))
