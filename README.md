WikiSpy
=======

WikiSpy is a website that allows you to find all changes done by a specified
domain on a website powered by MediaWiki (e.g. Wikipedia). You can use it for
example to see what part of Wikipedia a given company edited and sometimes spot
interesting propaganda being added.

Here you can browse the code that powers the website. If you would like to take
a look at the actual website, you will have to wait until the author finally
brings it up. I will update this document and point there when it happens.

Depencencies
============

1. Python 2
2. django 1.8 or newer
3. psycopg2, psycopg2ct or psycopg2cffi
4. PostgreSQL

There might be more dependencies that I had not listed yet.


Installation
============

rDNS table
----------

The process so far takes about 110GiB of space (80GiB data, 30GiB indexes) and
only has to be done once, not necessarily on the target server. On my computer
(i7-3770, non-SSD drive, 8GiB RAM) it took about six hours to perform this
step.

The project requires a PostgreSQL database and the data set from Rapid7 "Sonar"
project. You can download it here: https://scans.io/study/sonar.rdns

Create the table using the following SQL command:

```
CREATE TABLE wikispy_rdns(ip INET, rdns TEXT);
```

Load the .gz rDNS archive without duplicates. I used the following command for
that:

```
pv 20150311-rdns.gz | \
pigz -d | \
pypy ./make-rdns.py | \
psql -c 'COPY wikispy_rdns FROM stdin'
```

"pv" is just there to show you a progress bar. You can replace it with "cat".
Now create an index:

```
ALTER TABLE wikispy_rdns ADD PRIMARY KEY(ip);
```

Wikipedia article parsing
-------------------------

Now we can download a Wiki and extract anonymous changes from it. You can
(but don't have to) use a different machine other than the one you used before
for that since the process doesn't depend on rDNS table. Let's use etree for
article parsing:

```
wget https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-meta-history.xml.7z
7z x -so simplewiki-latest-pages-meta-history.xml.7z 2>/dev/null | etree.py > out.json
cut -d'"' -f4 < out.json | uniq | sort | uniq > unique_ips.txt
```

Wikipedia rDNS matching
-----------------------

Now, let's go back to the host where we did the rDNS matching. If you're
using multiple hosts, copy the unique\_ips.txt file generated in the previous
process. Regardless of that, run the following commands:

```
psql -c 'COPY rdns_me FROM STDIN' < unique_ips.txt
psql -c 'DROP TABLE IF EXISTS rdns_me; CREATE TABLE rdns_me(ip inet)'
psql -c 'COPY (SELECT r.* from rdns_me t JOIN wikispy_rdns r ON t.ip=r.ip) TO STDOUT;' > rdns.txt
```

The final command took 15 minutes on my PC.

```
./bulkload-copy.py 1 rdns.txt < out.json | sed -e 's@\\@\\\\@g' > copy.sql
```

Importing the generated data
----------------------------

This has to be done on the production server. If you're not there, copy file
"copy.sql" from the previous process.

Now, remove any indexes and constraints for wikispy\_edit if this is not your
first bulk import. Once you have done that, insert a Wiki and bulk load the
data, after which you should restore the indexes:

```
# TODO: explain how to remove the indexes
psql -c "INSERT INTO wikispy_wiki VALUES (1, 'simplewiki', 'simple', 'wikipedia.org');"
psql -c 'COPY wikispy_edit (wikipedia_edit_id, title, wiki_id, ip, time, view_count, rdns) FROM STDIN' < copy.sql
# TODO: explain how to restore the indexes
```

Unless I messed up this HOWTO, this should be enough to start up the site. Now,
compile translations:

```
./manage.py compilemessages
```

Security notes
==============

Please take the following steps in order to increase the security of the
website:

1. In settings.py, change SECRET\_KEY to a random value and DEBUG to False,
2. Revoke PostgreSQL access to the COPY command in case of an SQL injection.
