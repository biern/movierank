# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from cache import load_cache, store_cache
from databases import FilmwebDatabase
from outputs import HTMLOutput
from utils import create_parser, find_movies_info, histogram


def main():
    logging.basicConfig(level=logging.DEBUG)
    # Parser and args
    parser = create_parser()
    args = parser.parse_args()
    # Setup resources and dirs
    dest = open(args.out, 'w')
    res_dir = os.path.split(os.path.abspath(__file__))[0]
    template = open(os.path.join(res_dir, 'template.html'), 'r').read()
    output = HTMLOutput(dest, template)
    cache_dir = os.path.split(args.out)[0]
    # Use cache
    dbs = [FilmwebDatabase()]
    if not args.force:
        cache = load_cache(cache_dir, args.out)
        if cache:
            logging.info("using cache file")
            dbs = cache

    # Get movies
    movies = find_movies_info(args.dirs, dbs, output, '-rating')

    # Histogram?
    if args.histogram:
        path = os.path.join(cache_dir, '.movierank-histogram.png')
        histogram(movies, path)
        output.add_extra('histogram', path)

    # Finish
    store_cache(cache_dir, dbs, suffix=args.out)
    output.flush()

    # Run browser?
    if args.run:
        subprocess.Popen(["xdg-open", args.out],
                         stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE)

if __name__ == "__main__":
    main()
