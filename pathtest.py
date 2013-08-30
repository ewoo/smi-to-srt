#!/opt/local/bin/python
# -*- coding: utf-8 -*-

"""
Converts SMI formatted subtitle files to SRT.
Usage: pathtest.py [-vdo FILE] SOURCE [-uf][TARGET]

-v --verbose  Show logging info
-d --debug    Ouput debugging info and save conversion data
-o FILE       Output conversion data file [default: ./conversiondata.txt]
SOURCE        The SAMI formatted subtitle file you want to convert. Example: movie.smi
-u --unicode  Attempt to convert from local charset to unicode
-f --force    Force best-guess conversion local charset to unicode
TARGET        Name of the converted file
"""
import sys
import os.path
from docopt import docopt


def main(arguments):
	print arguments


if __name__ == 'main':
	arguments = docopt(__doc__, version="script 1.0")
	main(arguments)