#!/usr/bin/python

"""
Reads the Wikipedia history dump format and extracts anonymous edits out of it,
turning them into a stream of one-line JSON dictionaries.

USAGE: 7z x -so plwiki-20150219-pages-meta-history1.xml.7z 2>&1 | \
    ./etree.py > out.json

AUTHOR: Jacek Wielemborek, licensed under WTFPL.
"""

import xml.etree.cElementTree as ET
import sys
import bz2
import re
import urllib
import json

IP_RE_STR = ("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25"
             "[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]"
             "\\d|25[0-5])$")
IP_RE = re.compile(IP_RE_STR)
TAG_PREFIX = "{http://www.mediawiki.org/xml/export-0.10/}"

def handle_tuple(ip, title, timestamp, id_):
    if not IP_RE.match(ip):
        return
    title_quoted = urllib.quote(title.encode('utf8'))
    d = {}
    d['ip'] = ip
    d['title'] = title
    d['id'] = id_
    d['timestamp'] = timestamp
    j = json.dumps(d)
    print(j)


def parse_file(f):
    title = None
    i = 0
    for event, element in ET.iterparse(f):
        if element.tag == TAG_PREFIX + "timestamp":
            timestamp = ''.join(element.itertext())
        if element.tag == TAG_PREFIX + "id":
            id_ = ''.join(element.itertext())
        if element.tag == TAG_PREFIX + "title":
            title = ''.join(element.itertext())
        if element.tag ==  TAG_PREFIX + "ip":
            ip = ''.join(element.itertext())
            handle_tuple(ip, title, timestamp, id_)
        element.clear()

if __name__ == "__main__":
    parse_file(sys.stdin)
