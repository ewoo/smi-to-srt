smi-to-srt
==========

A command line tool to convert smi to srt subtitle files.

Usage
-----
- Ensure your source file (filename.smi) is saved in utf-8 encoding. (See below)
- Run the following command `$ python smi-to-srt.py file-to-convert.smi output-file.srt`

Features
--------
- Automagic detect local charset to UTF-8 conversion (courtesy of chardet.universaldetector)
- Retains supported font styling elements specified in source

Known Bugs
----------
- Fails when BODY element starts with a bunch of blank lines
  (Needs more robust start element seeking logic--during processing)
- Does not intelligently assigns missing end timestamps
  (Simply assigns 2 second duration--without considering next dialog line)

Areas for Improvement
---------------------
- Better missing end marker (duration) calculation
- Some code to properly package dependencies
- Much more pythonic refactoring needed
