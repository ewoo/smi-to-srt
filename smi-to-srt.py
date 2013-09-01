#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Converts SMI formatted subtitle files to SRT.

Usage: 
pathtest.py --version
pathtest.py [-vdo FILE] SOURCE [-uf][TARGET]

--version     Version number
-v --verbose  Show logging info
-d --debug    Ouput debugging info and save conversion data
-o FILE       Output conversion data file [default: ./conversiondata.txt]
SOURCE        The SAMI formatted subtitle file you want to convert. Example: movie.smi
-u --unicode  Convert from local charset and save as unicode
-f --force    Force best-guess conversion local charset to unicode
TARGET        Name of the converted file
"""

import sys
import re
import codecs
import datetime
from docopt import docopt
import os.path
from os.path import expanduser

# Globals
VERBOSE = False
CONVERT_TO_UNICODE = False

def main(args):

    global VERBOSE, CONVERT_TO_UNICODE
    VERBOSE = args["--verbose"]
    CONVERT_TO_UNICODE = args["--unicode"]

    # Set filepaths.
    src_file = os.path.abspath(args["SOURCE"])

    # If none privided, build target file name.
    if args["TARGET"] is None:
        filename, ext = os.path.splitext(src_file)
        target_file = filename + ".srt"
    else:
        target_file = os.path.abspath(args["TARGET"])

    sourceLines = import_lines_from_SAMIfile(src_file)
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
    write_to_file(target_file, exportlines)

    if VERBOSE:
        print "Conversion completed. %s" % target_file


class SummaryReport(object):
    """docstring for SummaryReport"""
    def __init__(self, arg):
        super(SummaryReport, self).__init__()
        self.arg = arg
        
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

        global VERBOSE
        if VERBOSE:
            print index
            print "%s --> %s" % (start, end)
            print item["content"]

        srtlines.append("%s%s" % (index, os.linesep))
        srtlines.append("%s --> %s" % (start, end))
#        srtlines.append("%s --> %s%s" % (start, end, os.linesep))
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


def milliseconds_to_timestamp(ms):
    timestamp = datetime.timedelta(milliseconds=ms)
    if len(str(timestamp)) < 9:
        timestamp = str(timestamp) + ",000"
    else:
        timestamp = str(timestamp).replace(".",",")[:-3] # Lose a bit of precision?
    
    timestamp = timestamp.zfill(12)
    return timestamp


def dump_results(resultdict):
    for i, v in resultdict.iteritems():
        print i, v
        print v["content"]


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
    global VERBOSE, CONVERT_TO_UNICODE
    if VERBOSE:
        print filepath

    try:
        if CONVERT_TO_UNICODE:
            fo = codecs.open(filepath, "r", "utf-8")
        else:
            fo = codecs.open(filepath, "r")
        lines = fo.readlines()
        fo.close()
    except IOError:
        log_error_and_quit(sys.exc_info())
    return lines

def write_to_file(filepath, lines):
    global CONVERT_TO_UNICODE
    if CONVERT_TO_UNICODE:
        fw = codecs.open(filepath, "w+", "utf-8-sig")
    else:
        fw = codecs.open(filepath, "w+")        
    fw.writelines(lines)
    fw.close()
    return


def log_error_and_quit(error):
    if error[1][1]:
        print "Uh oh. Failed to convert file. %s" % error[1][1]
    else:
        print "Sorry, something wen terribly wrong."
    sys.exit(-1)


# Function to extract timestamp
def extract_timestamp(line):
  regex = re.compile("Start=(\d+)")
  match = regex.search(line)
  if match:
    return int(match.group(1))


def extract_dialog(line):
    global VERBOSE
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
    args = docopt(__doc__, version="smi-to-srt version 0.85")
    main(args)