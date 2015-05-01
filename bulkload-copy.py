#!/usr/bin/env python
import sys

wiki_id = int(sys.argv[1])

f = open(sys.argv[2])
d = {}
sys.stderr.write("Hold tight, I'm going to load the rDNS table... do NOT "
                 "reboot on freezes, this might freeze for a few minutes.\n")
for line in f:
  x = line.rstrip().split("\t")
  d[x[0]] = x[1]
sys.stderr.write("Loading done!\n")

import json
#copy wikispy_edit(ip, wikipedia_edit_id, time, title, wiki_id, view_count)
#wiki_id
#2       39434507        Chiricahua      1       5.226.116.132   2014-05-12 13:36:27+02  0       5-226-116-132.static.ip.netia.com.pl
#{"ip": "82.135.241.109", "id": "294547127", "timestamp": "2009-06-05T09:42:24Z", "title": "M\u0101ris Martinsons (director)"}

lines = no_rdns = 0
for line in sys.stdin:
    lines += 1
    j = json.loads(line.rstrip())
    rdns = d.get(j['ip'])
    if rdns is None:
        no_rdns += 1
        continue
    print("\t".join([j['id'], j['title'], str(wiki_id), j['ip'], j['timestamp'], "0", rdns]))
sys.stderr.write("Done. Parsed %d lines, %d had no rdns.\n" % (lines, no_rdns))
