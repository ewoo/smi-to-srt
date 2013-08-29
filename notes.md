Project Notes
=============

Time Log
--------
40 mins
40 mins
75 mins
45 mins
30 mins

Total: about 4 hours

Next Items
----------
- convert <br> into line-endings (Windows?)

    >>> import re
    >>> guff = """<atag>\r\n<bt\r\nag c="2">"""
    >>> re.sub(r"(<[^>]*)\r\n([^>]*>)", r"\1\2", guff)
    '<atag>\r\n<btag c="2">'
    >>>

- Add two zero padding
- preserve multiline
- keep `<font color=>` tags? and keep supported tags like `<b>` and `<i>`
- investigate broken tags
- Microsoft CP-1252 (default text format)
- refactor

Lower Priority
--------------
- set default constant to reasonable amount


Features to Add
---------------
- Local charset detection
- Toggle on-off

Completed Items
---------------
- compute dialog display times
- compute missing endtimes--mark these as "computed": true


NOTES
=====
First convert raw lines into a dictionary indexed by their order:


	{ 
		345: "<SYNC Start=5879709><P Class=KRCC>\r\n",
		346: "\xeb\xb0\x98\xeb\xa9\xb4 \xed\x83\x9c\xeb\x8f\x84\xeb\x8a\x94 \xec\x97\xbd\xec\xa0\x84\xea\xb3\xbc \xea\xb0\x99\xec\x95\x84\xec\x95\xbc \xed\x95\x9c\xeb\x8b\xa4.\r\n",
		347: "<SYNC Start=5865876><P Class=KRCC>&nbsp;\r\n"
	}	


This is how the intermediate structure should look like:

    { 
    	345:
    	{
    		"type": "start"
    		"start": 3894855, 
    		"end": None, 
    		"dialog": "\r"
    	},	
    	346:
    	{ 
    		"type": "content"
    		"start": None, 
    		"end": None, 
    		"dialog": "You said that everything would be OK!\r"
    	},
    	347:
    	{ 
    		"type": "end"
    		"start": None, 
    		"end": 3896475, 
    		"dialog": "&nbsp;\r"
    	}
    }

Processing:
- Collapse entries w/o start times into their closest parent entry

    # Make into dictionary with index as keys
    >>> d = { i:val for i, val in enumerate(lines) }

    # Function to extract timestamp
    def extract_timestamp(content):
      regex = re.compile("Start=(\d+)")
      match = regex.search(content)
      if match:
      	return int(match.group(1))

    # Build new list
    [extract(v) for k, v in l.iteritems()]

    # Convert timestamp to timedelta and reformat
    delta = datetime.timedelta(milliseconds=5885584)
    reformatted = str(delta).replace(".",",")[:-3]


    def ec(line):
      regex = re.compile("<[p|P][^>]*>(.*$)")
      match = regex.search(line)
      if match:
    	return match.group(1).rstrip(os.linesep)
      else:
      	return line.rstrip(os.linesep)


    # Build dictionary

    for l in dialog:
        if "<SYNC " in l and not linesopen:
            linesopen = true
            # beginstamp = Start=617126
            # get begin stamp, convert to timedelta
            # collect lines-text = content

            lastlinesstamp = delta
        if "<SYNC + nbsp" in l:
            # grab endstamp
            linesopen = false

    if linesopen:
        # close out lines

    d = [{key:value} for (key,value) in enumerate(dialog)]


    #Write out the liness