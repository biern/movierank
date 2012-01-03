# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from databases import FilmwebDatabase
from outputs import HTMLOutput
from utils import create_parser, find_movies_info


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = create_parser()
    args = parser.parse_args()

    dest = open(args.out, 'w')
    res_dir = os.path.split(os.path.abspath(__file__))[0]
    template = open(os.path.join(res_dir, 'template.html'), 'r').read()

    find_movies_info(args.dirs,
                    [FilmwebDatabase()],
                     HTMLOutput(dest, template), '-rating')
    if args.run:
        subprocess.Popen(["xdg-open", args.out],
                         stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE)

if __name__ == "__main__":
    main()
