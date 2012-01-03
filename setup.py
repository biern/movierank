#!/usr/bin/env python
#-*- coding: utf-8 -*-

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

import os

here = os.path.abspath(os.path.dirname(__file__))
NAME = "movierate"
VERSION = open(os.path.join(here, 'VERSION')).read()
README = open(os.path.join(here, 'README.rst')).read()
NEWS = ""


install_requires = [

]

setup(name=NAME,
      version=VERSION,
      entry_points={
        'console_scripts': [
            'movierate = movierate.movierate:main'
            ]
        },
      packages=find_packages('src'),
      package_dir={'': 'src'},
      package_data={'movierate': ['template.html']},
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      description="{}".format(NAME),
      long_description=README + '\n\n' + NEWS,
      keywords='{}'.format(NAME),
)
