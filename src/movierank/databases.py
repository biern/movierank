# -*- coding: utf-8 -*-

import getpass
import logging
import lxml.html
from lxml.cssselect import CSSSelector
from lxml import etree
import mechanize
import urllib
import re
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
    logged_in = False
    log = logging.getLogger("FilmWebDB")

    def __init__(self, force_reload=False):
        self._init_browser()
        self._force_reload = force_reload
        self.movies = {}
        self.not_found = []

    def _init_browser(self):
        self.br = mechanize.Browser()
        # Skips ad later
        self.br.open("http://www.filmweb.pl")

    def _open_movie_site(self, title, title_hints):
        url = "http://www.filmweb.pl/search/film?q={}".format(
            urllib.quote(title))
        response = self.br.open(url)
        time.sleep(1)
        text = response.read()
        html = etree.HTML(text)
        title_nodes = CSSSelector(".searchResultTitle")(html)
        # Not found
        if len(title_nodes) == 0:
            self.log.info('Not found'.format(title))
            self.not_found.append(title)
            return None

        # Try to match movie year with results
        year = title_hints.get('year')
        if len(title_nodes) > 1 and year:
            year_nodes = CSSSelector(".searchResultDetails")(html)
            for tn, yn in zip(title_nodes, year_nodes):
                m_year = re.search(r"(\d{4})", yn.text)
                if m_year and m_year.group(1) == year:
                    node = tn
                    break
            else:
                node = title_nodes[0]
        else:
            node = title_nodes[0]

        return self.br.open(node.get('href'))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['br']
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self._init_browser()

    def login(self, login, password=None):
        if password == None:
            password = getpass.getpass()

        url = "https://ssl.filmweb.pl/login"
        self.br.open(url)
        self.br.select_form(name="form")
        self.br["j_username"] = login
        self.br["j_password"] = password
        response = self.br.submit()
        self.logged_in = response.geturl() == "http://www.filmweb.pl/"
        time.sleep(1)
        return self.logged_in

    def find_movie(self, title, title_hints={}):
        # Use cache if possible
        if not self._force_reload:
            try:
                return self.movies[title]
            except KeyError:
                if title in self.not_found:
                    return None

        self.log.info('Searching for "{}"'.format(title))
        response = self._open_movie_site(title, title_hints)
        if not response:
            return None

        data = {}
        url = response.geturl()
        html = etree.HTML(response.read())

        data['url'] = url
        data['title'] = CSSSelector("h1.pageTitle a")(html)[0].get('title')
        data['genres'] = ", ".join(n.text for n in CSSSelector(
            ".basic-info-wrapper table tr:first-child+tr td a")(html))
        # if self.logged_in:
        #     # .recomVal relies on js :-(
        #     data['recomval'] = CSSSelector(".recomVal")(html)[0].text

        node = CSSSelector(".rates strong span")(html)
        data['rating'] = node[0].text.replace(",", ".")

        for k, v in data.items():
            data[k] = v.encode('utf-8')

        result = title_hints.copy()
        result.update(data)

        self.movies[title] = result
        return result

    def movie_values(self, key):
        movie = self.movies[key]
        return [
            {'text': movie.get('rating'), 'href': movie.get('url')}
            ]

    def headers(self):
        return [
            '★'
            ]
