#!/usr/bin/env python

"""
Looks for anonymous edits in the output of bot.py, gets their rDNS and prints
the results in the JSON output format.

Example:

If the bot.py output is being redirected to out.json, we can do:
$ tail -f out.json | python parse.py

More output should follow. The JSON line was split for readability purposes.

Author: Jacek Wielemborek, licensed under WTFPL.
"""

import sys
import re
import socket
import json
import os

MATCH_REGEX = ('^\x0314\[\[\x0307(.*?)\x0314\]\]\x034 .*?\x0310 \x0302(.*?)'
    '\x03 \x035\*\x03 \x0303(.*?)\x03 \x035\*\x03 \(\+?(.*?)\) \x0310(.*?)'
    '\x03\n?$'
)
MATCH_TITLES = ['title', 'diff_url', 'ip', 'change_size']

# make stdout unbuffered
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


def handle_message(skip_rdns, channel, now, payload):

    match = re.match(MATCH_REGEX, payload)
    if match is None:
        sys.stderr.write("No match: %s, %s\n" % (channel, repr(payload)))
        return

    json_dict = {MATCH_TITLES[i]: match.groups()[i]
                 for i in range(len(MATCH_TITLES))}


    if not valid_ip(json_dict['ip']):
        return
    if not skip_rdns:
        try:
            json_dict['rdns'] = socket.gethostbyaddr(json_dict['ip'])[0]
        except socket.herror:  # [Errno 1] Unknown host
            pass
        except socket.gaierror:  # [Errno -2] Name or service not known
            pass

    del json_dict['change_size']
    change_id = re.findall('diff=([0-9]+)&', json_dict['diff_url'])
    if not change_id:
        sys.stderr.write("WTF: unparsable URL: %s\n" % json_dict['diff_url'])
        return
    else:
        json_dict['id'] = change_id[0]
        del json_dict['diff_url']
    json_dict['timestamp'] = now
    json_dict['channel'] = channel

    print(json.dumps(json_dict))


def main(skip_rdns):
    for line in sys.stdin:
        if not line.startswith('{'):
            continue
        handle_message(skip_rdns, **json.loads(line))

if __name__ == '__main__':
    main(len(sys.argv) > 1)
