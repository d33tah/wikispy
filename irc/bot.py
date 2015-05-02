#!/usr/bin/env python

"""
Watches for a given list of IRC channels and prints any line seen on any of
them with a timestamp in JSON format.

Example:

$ python bot.py irc.wikimedia.org 6667 'wikispy' '#en.wikipedia' '#pl.wikipedia' | head -n1
Connecting...
Connected.
{"now": "2015-05-02T14:55:17.863639", "payload": "test", "channel": "#en.wikipedia"}
(traceback related to head -n1 closing the pipe)

The output is meant to be consumed by parse.py.

Author: Jacek Wielemborek, licensed under WTFPL.
"""

import sys
import argparse
import itertools
import datetime
import uuid
import re
import socket
import json
import os

import irc.client

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False

def on_connect(connection, event):
    sys.stderr.write("Connected.\n")
    for channel in sys.argv[4:]:
        connection.join(channel)

def on_disconnect(connection, event):
    raise SystemExit()

def on_pubmsg(connection, msg):

    if len(msg.arguments) != 1:
        return

    payload = msg.arguments[0]
    now = str(datetime.datetime.utcnow().isoformat())
    channel = msg.target
    print(json.dumps({'now': now, 'channel': channel, 'payload': payload}))

def main():
    reactor = irc.client.Reactor()
    try:
        sys.stderr.write("Connecting...\n")
        c = reactor.server().connect(sys.argv[1], int(sys.argv[2]),
                                     sys.argv[3] + str(uuid.uuid4()))
    except irc.client.ServerConnectionError:
        print(sys.exc_info()[1])
        raise SystemExit(1)

    c.add_global_handler("welcome", on_connect)
    c.add_global_handler("disconnect", on_disconnect)
    c.add_global_handler("pubmsg", on_pubmsg)

    reactor.process_forever()

if __name__ == '__main__':
    main()
