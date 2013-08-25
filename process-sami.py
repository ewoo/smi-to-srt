#!/usr/bin/python

# http://en.wikipedia.org/wiki/SAMI
# From .smi (SAMI subtitle format)
# <SYNC START=8247741>
#     <P CLASS=SUBTTL>I’ve left my<br>new torch in Narnia.
#  <SYNC START=8250007>
#     <P CLASS=SUBTTL>&nbsp;

# http://en.wikipedia.org/wiki/SubRip
# To .srt (SubRip subtitle format)
# 931
# 02:17:27,741 --> 02:17:30,007
# I’ve left my
# new torch in Narnia.

# Open file.
import os.path
import re
from os.path import expanduser

filename = "sami.txt"

home = expanduser("~")
filepath = os.path.join(home, filename)

fo = open(filepath, "rw+")
line = fo.readlines()
fo.close()

regex = re.compile(r"<sync", re.IGNORECASE)
res = regex.match(line[17])