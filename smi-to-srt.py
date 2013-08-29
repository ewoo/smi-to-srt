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
import datetime
from os.path import expanduser

SOURCE_FILENAME = "sami.txt"
TARGET_FILENAME = "output.srt"

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

    for key, item in results.iteritems():
        if item["end"] is not None:
            item["duration"] = (item["end"] - item["start"])/1000.0 
        else:
            item["end"] = item["start"] + 2000 


    # print "Summary"
    # print "======="
    # print "%s totals lines to start" % len(d)
    # print "..."
    # print "%s content lines collapsed" % len(removed_content_items)
    # print "%s end lines collapsed" % len(removed_end_items)
    # print "..."
    # print "%s start lines dialog" % len(results)
    # print "%s without end times" % (len(results) - len(removed_end_items))

    # for key, item in results.iteritems():
    #     #print key, item
    #     if item.get("duration") is not None:
    #         print "key: %s duration: %.2g secs" % (key, item.get("duration"))
    #     else:
    #         print "key: %s duration: None" % (key)
    #     print item["content"]


    # Format results into SRT.
    index = 1
    exportlines = []

    for key, item in results.iteritems():

        start = milliseconds_to_timestamp(item["start"])
        end = milliseconds_to_timestamp(item["end"]) if item["end"] is not None else None

        print index
        print "%s --> %s" % (start, end)
        print item["content"]
        print ""

        exportlines.append("%s%s" % (index, os.linesep))
        exportlines.append("%s --> %s%s" % (start, end, os.linesep))
        exportlines.append("%s%s" % (item["content"], os.linesep))
#        exportlines.append("%s" % os.linesep)

        index = index + 1

    # Write to file...
    write_to_file(os.path.join(home, TARGET_FILENAME), exportlines)

def milliseconds_to_timestamp(ms):
    timestamp = datetime.timedelta(milliseconds=ms)
    timestamp = str(timestamp).replace(".",",")[:-3] # Lose a bit of precision?
    return timestamp


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

def write_to_file(filepath, lines):
    fw = codecs.open(filepath, "w+", "utf-8-sig")
    fw.writelines(lines)
    fw.close()
    return

# Function to extract timestamp
def extract_timestamp(line):
  regex = re.compile("Start=(\d+)")
  match = regex.search(line)
  if match:
    return int(match.group(1))


def extract_dialog(line):
    print ""
    print "before: %s" % line  
    # Extract inner text from <P> tag
    regex = re.compile("<[p|P][^>]*>(.*$)")
    # line = re.sub(r"/^<([a-z]+)([^<]+)*(?:>(.*)<\/\1>|\s+\/>)$/", "", line)
    match = regex.search(line)
    if match:
        # TOOD: Replace only \r\n (windows style) with \n
        line = match.group(1)

    # Remove <br> tags
    line = re.sub("<[B|b][r|R]>", "", line)

    # regex = re.compile("<font")
    # match = regex.search(line)
    # # If there are open font tags, close them
    # if match:
    #     line = line + "</font>" 

    print "after: %s" % line
    return line


def is_clearing_line(line):
    regex = re.compile("\&nbsp;")
    match = regex.search(line)
    if match:
        return True
    else:
        return False


if __name__ == "__main__":
    main()