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

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import datetime
import sys
import json
import uuid


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "%s-%s" % (sys.argv[3], str(uuid.uuid4()))

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for channel in sys.argv[4:]:
            self.join(channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""

        now = str(datetime.datetime.utcnow().isoformat())
        print(json.dumps({'channel': channel, 'now': now, 'payload': msg}))
        sys.stdout.flush()


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        sys.stderr.write("Connection failed: %s. Reconnecting.\n" % reason)


if __name__ == '__main__':
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), LogBotFactory())
    reactor.run()
