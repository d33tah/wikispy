#!/usr/bin/python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikispy.settings")

from wikispy.models import Edit
import ast
import sys
from django.db import transaction

def main():
    with transaction.atomic():
        for line in sys.stdin:
            fields = ast.literal_eval(line)
            e = Edit()
            e.wikipedia_id = int(fields[-1].split('=')[-1])
            e.save()

if __name__ == "__main__":
    main()
