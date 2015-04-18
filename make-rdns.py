#!/usr/bin/pypy

"""
Converts Rapid7's "Sonar" rDNS data into a form suitable for importing into a
database. Removes multiple values for a single IP and gets rid of malformed
entries.

Author: Jacek Wielemborek, licensed under WTFPL.
"""

import sys
import struct
import socket
import base64

last_ip = None
last_rdns = None
try:
    for line in sys.stdin:
        line = line.rstrip("\r\n")
        idx = line.find(',')
        ip = line[:idx]
        rdns = line[idx+1:]
        if not rdns.replace('.', '').replace('-', '').isalnum():
            continue
        if ip != last_ip:
            print("%s\t%s" % (ip, rdns))
        last_ip = ip
        last_rdns = rdns
except Exception, e:
    if isinstance(e, IOError):
        sys.exit(1)
    sys.stderr.write(line)
    raise
