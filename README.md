smi-to-srt
==========

Command Line tool to convert smi to srt subtitle files.

Usage
-----
- Ensure your source file (filename.smi) is saved in utf-8 encoding. (See below)
- Run the following command `$ python smi-to-srt.py file-to-convert.smi output-file.srt`

Known Bugs
----------
- Not yet removing `<br>` elements from dialog text.
- Not yet saving output to file.

Coming Features
---------------
- Automagic detect local charset to UTF-8 conversion (courtesy of chardet.universaldetector)
- Retain supported font styling elements specified in source
