# -*- coding: utf-8 -*-

import logging
from lxml.cssselect import CSSSelector
from lxml import etree
import mechanize
import urllib
import time


class MovieDatabase(object):
    def __init__(self):
        self.movies = {}
        self.not_found = []

    def movie_basic_info(self, key):
        movie = self.movies[key]
        return {
            'text': movie['title'],
            'sub': (movie.get('genres', ''),
                    movie.get('path', '') + '\n')
            }

    def find_movie(self, title, title_hints={}):
        pass

    def headers_info(self, movie):
        pass

    def movie_info(self):
        pass


class FilmwebDatabase(MovieDatabase):
    # TODO: login, %, seen
    logged_in = False
    log = logging.getLogger("FilmWebDB")

    def __init__(self):
        self._init_browser()
        self.movies = {}
        self.not_found = []

    def _init_browser(self):
        self.br = mechanize.Browser()
        # Skips ad later
        self.br.open("http://www.filmweb.pl")

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['br']
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self._init_browser()

    def find_movie(self, title, title_hints={}):
        self.log.info('Searching for "{}"'.format(title))
        url = "http://www.filmweb.pl/search/film?q={}".format(
            urllib.quote(title))
        response = self.br.open(url)
        time.sleep(1)
        text = response.read()
        html = etree.HTML(text)
        nodes = CSSSelector(".searchResultTitle")(html)
        if len(nodes) == 0:
            self.log.info('Not found'.format(title))
            self.not_found.append(title)
            return None

        result = {}

        node = nodes[0]
        response = self.br.open(node.get('href'))
        url = response.geturl()
        html = etree.HTML(response.read())

        result['url'] = url
        result['title'] = CSSSelector("h1.pageTitle a")(html)[0].get('title')
        result['genres'] = ", ".join(n.text for n in CSSSelector(
            ".basic-info-wrapper table tr:first-child+tr td a")(html))
        if self.logged_in:
            result['recomval'] = CSSSelector(".recomVal")(html)[0].text

        node = CSSSelector(".rates strong span")(html)
        result['rating'] = node[0].text.replace(",", ".")

        for k, v in result.items():
            result[k] = v.encode('utf-8')

        self.movies[title] = (result)
        return result

    def movie_info(self, key):
        movie = self.movies[key]
        return [
            {'text': movie.get('rating'), 'href': movie.get('url')}
            ]

    def headers_info(self):
        return [
            '★'
            ]
