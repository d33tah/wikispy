WikiSpy
=======

WikiSpy is a website that allows you to find all changes done by a specified
domain. You can use it for example to see what part of Wikipedia a given
company edited and sometimes spot interesting propaganda being added.

Here you can browse the code that powers the website. If you would like to take
a look at the actual website, you will have to wait until the author finally
brings it up. I will update this document and point there when it happens.

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

REMEMBER TO CHANGE SECRET_KEY IN SETTINGS.PY!
