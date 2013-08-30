#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Converts SMI formatted subtitle files to SRT.
Usage: 
pathtest.py --version
pathtest.py [-vdo FILE] SOURCE [-uf][TARGET]

-v --verbose  Show logging info
-d --debug    Ouput debugging info and save conversion data
-o FILE       Output conversion data file [default: ./conversiondata.txt]
SOURCE        The SAMI formatted subtitle file you want to convert. Example: movie.smi
-u --unicode  Attempt to convert from local charset to unicode
-f --force    Force best-guess conversion local charset to unicode
TARGET        Name of the converted file
--version     Version number
"""

import os
from docopt import docopt

def main(args):
	fp = open(os.path.abspath(args["SOURCE"]), "r")
	lines = fp.readlines()
	fp.close()

	for line in lines:
		print line

if __name__ == "__main__":
	args = docopt(__doc__)
	main(args)