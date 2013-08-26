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

# Notes:
# In many cases, the dialog is cleared via nbsp;
# However, 

# Open file.
import os.path
import re
from os.path import expanduser

filename = "sami.txt"

home = expanduser("~")
filepath = os.path.join(home, filename)

fo = open(filepath, "rw+")
lines = fo.readliness()
fo.close()

regex = re.compile(r"<sync", re.IGNORECASE)
res = regex.match(lines[17])

for i, val in enumerate(lines):
    print i, val

# Get index of content area
start_index = [i for i, v in enumerate(lines) if "<BODY>" in v][0]
end_index = [i for i, v in enumerate(lines) if "</BODY>" in v][0]

if start_index and end_index is not None:
    dosomething
else:
    sys.exit(-1)

# Grab content area only
content = lines[start_index+1:end_index]

# Dictionary from contect area
d = { i:val for i, val in enumerate(lines) }


def process_lines(lines):
    

# Function to extract timestamp
def extract_timestamp(line):
  regex = re.compile("Start=(\d+)")
  match = regex.search(line)
  if match:
    return int(match.group(1))

def extract_dialog(line):
  regex = re.compile("<[p|P][^>]*>(.*$)")
  match = regex.search(line)
  if match:
    return match.group(1).rstrip(os.linesep)
  else:
    return line.rstrip(os.linesep)

def is_clearing_line(line):
    regex = re.compile("\&nbsp;")
    match = regex.search(line)
    if match:
        return True
    else:
        return False
