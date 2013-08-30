#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import os.path
import codecs
from os.path import expanduser
from chardet.universaldetector import UniversalDetector

SOURCE_FILENAME = "star.smi"
TARGET_FILENAME = "star-utf8.txt"

# Get file name and path.
home = expanduser("~")
filepath = os.path.join(home, SOURCE_FILENAME)
destpath = os.path.join(home, TARGET_FILENAME)

fp = open(filepath, "rb")
detector = UniversalDetector()

print "Reading file to detect encoding..."
for line in fp:
	line = line.replace(b'\r',b'')
	detector.feed(line)
	if detector.done:
		break

fp.close()
detector.close()

enc = detector.result["encoding"].replace('-','_').lower()

print "Encoding: %s" % detector.result["encoding"]
print "Confidence: {0:.0f}% ".format(detector.result["confidence"]*100)

print "Converting to UTF-8..."
fp = codecs.open(filepath, "r", enc)
lines = fp.readlines()
fp.close();

df = codecs.open(destpath, "w+", "utf-8-sig")
df.writelines(lines)
df.close()

print "Done."