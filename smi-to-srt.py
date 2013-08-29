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
VERBOSE = False

def main():
    
    # Get file name and path.
    home = expanduser("~")
    filepath = os.path.join(home, SOURCE_FILENAME)

    # Debug
    print filepath

    sourceLines = import_lines_from_SAMIfile(filepath)
    sourceLines = extract_dialog_lines(sourceLines)

    # Create dictionary processing.
    intermediateStore = build_intermediate_dict_from_lines(sourceLines)

    results = intermediateStore.copy()

    # TODO: Move this into a summary class.
    removed_content_items = {}
    removed_end_items = {}

    lastProcessedStartElementKey = None

    # Collate dialog content onto the start elements
    for key, item in intermediateStore.iteritems():
        if item["start"] is None and item["end"] is None:
            # Content item. Concat dialog content onto the last start item.
            results[lastProcessedStartElementKey]["content"] = results[lastProcessedStartElementKey]["content"] + item["content"]
            removed_content_items[key] = results.pop(key)
        elif item["end"] is None:
            lastProcessedStartElementKey = key
        else:
            # Dialog clear item. Move end time to closet parent start item.
            results[lastProcessedStartElementKey]["end"] = item["end"]
            removed_end_items[key] = results.pop(key)

    # Compute meta data that indicates duration of each dialog line--a sanity check.
    for key, item in results.iteritems():
        if item["end"] is not None:
            item["duration"] = (item["end"] - item["start"])/1000.0 
        else:
            # Fill-in missing end times!!
            item["end"] = item["start"] + 2000 

    # Format results into SRT.    
    exportlines = intermediate_dict_to_srtlines(results)

    # Write to file...
    write_to_file(os.path.join(home, TARGET_FILENAME), exportlines)

    # Display results summary.
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


def build_intermediate_dict_from_lines(linesList):
    # Build an indexed dictionary from list
    linesDict = { i:val for i, val in enumerate(linesList) }

    # Process lines in dictionary to build resulting intermediate storage structure.
    # See notes.md for example
    intermediate_dict = { k:{ "start":extract_timestamp(v), "content": extract_dialog(v) } for k, v in linesDict.iteritems() }
    intermediate_dict = mark_line_endings(intermediate_dict)

    return intermediate_dict

def intermediate_dict_to_srtlines(intermediate_dict):
    srtlines = []
    index = 1

    for key, item in intermediate_dict.iteritems():

        start = milliseconds_to_timestamp(item["start"])
        end = milliseconds_to_timestamp(item["end"]) if item["end"] is not None else None

        if VERBOSE:
            print index
            print "%s --> %s" % (start, end)
            print item["content"]

        srtlines.append("%s%s" % (index, os.linesep))
        srtlines.append("%s --> %s%s" % (start, end, os.linesep))
        srtlines.append("%s%s" % (item["content"], os.linesep))

        index = index + 1
    
    return srtlines


def extract_dialog_lines(allLines):
    dialogLines = None

    # Get index of <BODY> tags to get content area.
    startIndex = [i for i, v in enumerate(allLines) if "<BODY>" in v][0]
    endIndex = [i for i, v in enumerate(allLines) if "</BODY>" in v][0]

    if startIndex and endIndex is not None:
        # Grab content elements only.
        dialogLines = allLines[startIndex+1:endIndex]        

    return dialogLines


def log_to_screen(message):
    print message


def milliseconds_to_timestamp(ms):
    timestamp = datetime.timedelta(milliseconds=ms)
    timestamp = str(timestamp).replace(".",",")[:-3] # Lose a bit of precision?
    timestamp = timestamp.zfill(12)
    print timestamp
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


def mark_line_endings(shaped_dict):
    for k, v in shaped_dict.iteritems():
        # 
        if is_clearing_line(v["content"]):
            shaped_dict[k]["end"] = v["start"]
            shaped_dict[k]["start"] = None
        else:
            shaped_dict[k]["end"] = None            
    return shaped_dict


def import_lines_from_SAMIfile(filepath):
    # TODO: Convert from local charset to UTF-8
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

    if VERBOSE:
        print "before: %s" % line

    # Extract inner text from <P> tag
    regex = re.compile("<[p|P][^>]*>(.*$)")
    match = regex.search(line)
    if match:
        line = match.group(1)

    # Remove <br> tags
    line = re.sub("<[B|b][r|R]>", "", line)

    if VERBOSE:
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