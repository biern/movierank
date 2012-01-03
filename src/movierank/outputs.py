# -*- coding: utf-8 -*-

from collections import defaultdict
import re


class Output(object):
    order = None

    def write(self, dbs):
        self.write_headers(dbs)
        for t in self.order:
            self.write_movie(t, dbs)

    def write_not_found(self, not_found):
        pass

    def flush(self):
        pass


class HTMLOutput(Output):
    def __init__(self, file, template):
        self._template = template
        self._format_data = defaultdict(str)
        self.file = file

    def write_headers(self, dbs):
        headers = ["Tytuł"]
        for db in dbs:
            headers += db.headers_info()

        self._headers_n = len(headers)
        self._format_data['headers'] = "\n".join("<th>{}</th>".format(h)
                                                 for h in headers)

    def write_movie(self, key, dbs):
        values = []
        values.append(self._value_to_tag(
                dbs[0].movie_basic_info(key)))
        for db in dbs:
            mi = db.movie_info(key)
            for i, v in enumerate(mi):
                if not isinstance(v, str):
                    mi[i] = self._value_to_tag(v)

            values.extend(mi)

        self._format_data['movies'] += "<tr>" + \
            "\n".join(["<td>{}</td>".format(v) for v in values]) + \
            "</tr>"

    def _value_to_tag(self, v):
        text = v['text']
        if 'href' in v.keys():
            text = '<a href="{}">{}</a>'.format(
                v['href'], v['text'])
        if 'sub' in v.keys():
            sub = v['sub']
            if not isinstance(sub, str):
                sub = "<br>".join(sub)

            text += '<div class="sub">{}</div>'.format(sub)

        return text

    def write_not_found(self, not_found):
        for movie in not_found.values():
            # dirty
            self._format_data['not_found'] += "<tr>" + \
                "<td>{}</td>".format(self._value_to_tag(
                    {'text': movie['title'],
                     'sub': movie['path'] } )) + \
                "<td></td>" * self._headers_n + \
                "</tr>"

    def flush(self):
        def repl(match):
            return self._format_data.get(match.group(1), "")

        text = re.sub(r"\{\{\s*(.*?)\s*\}\}", repl, self._template)
        self.file.write(text)
        self.file.flush()
