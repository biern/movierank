# -*- coding: utf-8 -*-

import argparse
import logging
import os
import time
import re

# 1. List dirs
# 2. Get titles info
# 3. Get movie info for each title
# 4. Sort
# 5. Arrange and render

# TODO:
# - parser
# - local db cache?


log = logging.getLogger("movierate")


def get_title_hints(path):
    # Rules:
    # - Treat four digit number as year
    # - Remove everything in filename following first bracket or year
    exts = '(avi|mpg|mpeg|mkv|mp4|wmv)$'

    dir, title = os.path.split(path)
    title, ext = os.path.splitext(title)
    if not os.path.isdir(path):
        if not re.search(exts, path):
            return None

    year = None

    re_year = r"(?P<year>\d{4}|\(\d{4}\)|\[\d{4}\])"
    m = re.search(re_year, title)
    if m:
        year = m.group('year')
        title = title[:m.start('year')]

    for char in ('(', '[', '{'):
        pos = title.find(char)
        if pos >= 0:
            title = title[:pos]

    # title = re.sub(r'\(.*?\)', '', title)
    # title = re.sub(r'\[.*?\]', '', title)
    # title = re.sub(r'\{.*?\}', '', title)

    return {'title_raw': title, 'year': year, 'path': path}


def get_titles_hints(directories):
    titles_hints = []
    log.info("Searching for titles")
    for d in directories:
        log.info('entering dir {}'.format(d))
        files = os.listdir(d)
        for f in files:
            f = os.path.join(d, f)
            log.info('  checking "{}"'.format(f))
            title = get_title_hints(f)
            if title:
                titles_hints.append(title)

    return titles_hints


def find_movies_info(directories, dbs, output=None, sort_key='title'):
    """

    :param str outfile: If outfile is None then tmp file is used
    :returns: path to created file
    """
    db_main = dbs[0]
    not_found = {}
    titles_hints = get_titles_hints(directories)

    log.info("Getting movies information")
    for th in titles_hints:
        found = False
        for i, db in enumerate(dbs):
            # be nice
            time.sleep(1)
            movie = db.find_movie(th['title_raw'], th)
            if not movie:
                continue

            found = True
            if db == db_main:
                # Storing all information in db_main
                th.update(movie)
                movie.update(th)

        if not found:
            th['title'] = th['title_raw']
            not_found[th['title_raw']] = th

    # Sort according to 'sort_key' in db_main
    reverse = False
    if sort_key.startswith("-"):
        reverse = True
        sort_key = sort_key[1:]

    titles_found = [th for th in titles_hints \
                        if th['title_raw'] not in not_found.keys()]
    titles_sorted = [
        th['title_raw'] for th in \
            sorted(titles_found,
                   key=lambda i: db_main.movies[i['title_raw']][sort_key],
                   reverse=reverse)
        ]

    output.order = titles_sorted
    output.write(dbs)
    output.write_not_found(not_found)
    output.flush()


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', metavar="DIR", nargs='*', default=["."],
                        help='directories to search')
    parser.add_argument("-o", "--out",
                        help="output file (default: movierate.html)",
                        default="movierate.html")
    parser.add_argument("-r", "--run", help="open file in default viewer",
                        action="store_true")
    return parser
