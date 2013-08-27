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

    results = sd.copy()

    removed_content_items = {}
    removed_end_items = {}

    last_start_key = None

    for key, item in sd.iteritems():
        if item["start"] is None and item["end"] is None:
            # Content item. Concat dialog content onto the last start item.
            results[last_start_key]["content"] = results[last_start_key]["content"] + item["content"]
            removed_content_items[key] = results.pop(key)
        elif item["end"] is None:
            last_start_key = key
        else:
            # Dialog clear item. Move end time to closet parent start item.
            results[last_start_key]["end"] = item["end"]
            removed_end_items[key] = results.pop(key)

        #print "key: %s start: %s end: %s" % (key, sd[key]["start"], sd[key]["end"])

    print "Summary"
    print "======="
    print "%s totals lines to start" % len(d)
    print "..."
    print "%s content lines collapsed" % len(removed_content_items)
    print "%s end lines collapsed" % len(removed_end_items)
    print "..."
    print "%s start lines dialog" % len(results)
    print "%s without end times" % (len(results) - len(removed_end_items))


# tcharasika@greaterlouisville.com

        # if sd[key]["start"] == None and sd[key]["end"] == None:
        #     print "value %s" % i 
        #     parentkey = get_closest_start_line(sd, i)
        #     # print "Parent key: " + parentkey
        #     if parentkey is not None:
        #         sd[parentkey]["more_content"] = sd[parentkey]["content"] + v["content"]



def dump_results(resultdict):
    for i, v in resultdict.iteritems():
        print i, v
        print v["content"]


def process_lines(lines):
    print "Not implemented!"
    pass

def get_closest_start_line(dd, key):
    if dd.get(key)["start"] is not None:
        return key
    else:
        if key < 0:
            return None
        key = key - 1
        get_closest_start_line(dict, key)

def get_indexed_dict(thislist):
    # Dictionary from contect area
    d = { i:val for i, val in enumerate(thislist) }
    return d


def get_shaped_dict(ind):
    dd = { k:{ "start":extract_timestamp(v), "content": extract_dialog(v) } for k, v in ind.iteritems() }
    return dd


def mark_line_endings(shaped_dict):
    for k, v in shaped_dict.iteritems():
        # 
        if is_clearing_line(v["content"]):
            shaped_dict[k]["end"] = v["start"]
            shaped_dict[k]["start"] = None
        else:
            shaped_dict[k]["end"] = None            
    return shaped_dict


def mark_types(shaped_dict):
    pass


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