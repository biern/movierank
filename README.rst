About
=====

Python script that recognizes movie titles in given directories, finds them in online web services and generates HTML report with sorted titles, their ranking and links.

Installation
============

- Requires Python2.7 or higher.

::

        sudo python setup.py install

Usage examples:
===============

Show help::

        movierank -h

Scan current directory, generate 'movierank.html' report file and run it in browser (uses 'xdg-open' to determine browser)::

        movierank -r

Scan given directories write output to 'some_file.html' ::

        movierank some_dir/a some_other_dir . -o some_file.html

Force reloading every title, do not use cached data ::

         movierank -f

Generate histogram in report and show it (requires 'matplotlib' and 'numpy') ::

         movierank -r -hi
