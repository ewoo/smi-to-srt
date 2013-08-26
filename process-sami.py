#!/usr/bin/python
# -*- coding: utf-8 -*-

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
# In many cases, the dialog is cleared via <non-breaking space> nbsp;
# However, this may not always be the case!

# Open file.
import os.path
import codecs
import re
from os.path import expanduser

SOURCE_FILENAME = "sami.txt"
TARGET_FILENAME = "/Dropbox/smi_to_srt/sami.srt"

def main():
    # Get file name and path.
    home = expanduser("~")
    filepath = os.path.join(home, SOURCE_FILENAME)
    print filepath
    # Import lines into a list.
    lines = import_lines_from_file(filepath)

    # Get index of <BODY> tags to get content area.
    start_index = [i for i, v in enumerate(lines) if "<BODY>" in v][0]
    end_index = [i for i, v in enumerate(lines) if "</BODY>" in v][0]

    if start_index and end_index is not None:
        # Grab content elements only.
        dialoglines = lines[start_index+1:end_index]        
    else:
        sys.exit(-1)

    # Create dictionary processing.
    d = get_indexed_dict(dialoglines)

    # Process dictionary to build resulting strture.
    sd = get_shaped_dict(d)
    sd = mark_line_endings(sd)

    for i, v in sd.iteritems():
        print i, v
        print v["content"]


def process_lines(lines):
    print "Not implemented!"
    pass


def get_indexed_dict(list):
    # Dictionary from contect area
    d = { i:val for i, val in enumerate(list) }
    return d


def get_shaped_dict(dict):
    dd = { k:{ "start":extract_timestamp(v), "content": extract_dialog(v) } for k, v in dict.iteritems() }
    return dd


def mark_line_endings(shaped_dict):
    for k, v in shaped_dict.iteritems():
        # 
        if is_clearing_line(v["content"]):
            shaped_dict[k]["end"] = v["start"]
            shaped_dict[k]["start"] = None
    return shaped_dict

def import_lines_from_file(filepath):
    print filepath
    fo = codecs.open(filepath, "r", "utf-8")
    lines = fo.readlines()
    fo.close()
    return lines


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


if __name__ == "__main__":
    main()