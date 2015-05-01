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

The project requires a PostgreSQL database and the data set from Rapid7 "Sonar"
project. You can download it here: https://scans.io/study/sonar.rdns

Create the table using the following SQL command:

```
CREATE TABLE rdns(ip INET, rdns TEXT);
```

Load the .gz rDNS archive without duplicates. I used the following command for
that:

```
pv 20150311-rdns.gz | \
pigz -d | \
pypy ./make-rdns.py | \
psql -c 'COPY rdns FROM stdin'
```

Now create indexes:

```
ALTER TABLE wikispy_rdns ADD PRIMARY KEY(ip);
CREATE INDEX on wikispy_rdns(REVERSE(rdns) text_pattern_ops);
```

This can take up to 200GiB disk space.

(TODO: document importing Wiki anonymous changes)

Create indexes for Django-managed objects:
./manage.py sqlindex

Compile translations:
./manage.py compilemessages

REMEMBER TO CHANGE SECRET_KEY IN SETTINGS.PY!
