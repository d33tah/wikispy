#!/usr/bin/python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikispy.settings")

from wikispy.models import Edit, Wiki
import ast
import sys
from django.db import transaction

def main():
    with transaction.atomic():
        w = Wiki()
        w.name = "plwiki"
        w.save()
        for line in sys.stdin:
            fields = ast.literal_eval(line)
            e = Edit()
            e.ip = fields[0]
            e.title = fields[1]
            #e.time = fields[2]
            e.wikipedia_id = int(fields[-1].split('=')[-1])
            e.wiki = w
            e.save()

if __name__ == "__main__":
    main()
