#!/usr/bin/python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikispy.settings")

from wikispy.models import Edit, Wiki
import json
import sys
from django.db import transaction
try:
    import bdateutil.parser as dateparser
except ImportError:
    import dateutil.parser as dateparser

def main():
    if len(sys.argv) != 4:
        sys.exit("USAGE: %s <wikiname> <language> <domain>" % sys.argv[0])
    found = Wiki.objects.filter(name=sys.argv[1], language=sys.argv[2],
                                domain=sys.argv[3])
    if found:
        w = found[0]
    else:
        sys.exit("The Wiki is not in the database."
                 " Use add-wiki.py to fix that.")
    with transaction.atomic():
        for line in sys.stdin:
            parsed = json.loads(line)
            # {"ip": "81.43.234.228", "id": "378742081", "timestamp":
            #  "2010-08-13T17:25:26Z", "title": "User talk:Furret Boy"}
            e = Edit()
            e.ip = parsed['ip']
            e.title = parsed['title']
            e.time = dateparser.parse(parsed['timestamp'])
            e.wikipedia_edit_id = parsed['id']
            e.wiki = w
            e.save()

if __name__ == "__main__":
    main()
