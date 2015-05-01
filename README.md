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

"pv" is just there to show you a progress bar. You can replace it with "cat".
Now create an index:

```
ALTER TABLE wikispy_rdns ADD PRIMARY KEY(ip);
```

Now we can download a Wiki and extract anonymous changes from it. Let's use etree for that:

```
wget https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-meta-history.xml.7z
7z x -so simplewiki-latest-pages-meta-history.xml.7z  2>/dev/null | etree.py > out.json
psql -c 'DROP TABLE IF EXISTS rdns_me; CREATE TABLE rdns_me(ip inet)'
cut -d'"' -f4 < out.json | uniq | sort | uniq | psql -c 'COPY rdns_me FROM STDIN'
psql -c 'COPY (SELECT r.* from rdns_me t JOIN wikispy_rdns r ON t.ip=r.ip) TO STDOUT;' > rdns.txt
```

The final command took 15 minutes on my PC. Now, remove any indexes and
constraints for wikispy_edit. Once you have done that, insert a Wiki and bulk
load the data, after which you should restore the indexes:

```
# TODO: explain how to remove the indexes
./bulkload-copy.py 2 rdns.txt < out.json | sed -e 's@\\@\\\\@g' > copy.sql
psql -c "INSERT INTO wikispy_wiki VALUES (1, 'simplewiki', 'simple', 'wikipedia.org');"
psql -c 'COPY wikispy_edit (wikipedia_edit_id, title, wiki_id, ip, time, view_count, rdns) FROM STDIN' < copy.sql
# TODO: explain how to restore the indexes
```

Unless I messed up this HOWTO, this should be enough to start up the site. Now,
compile translations:

```
./manage.py compilemessages
```

*ALSO, REMEMBER TO CHANGE SECRET_KEY IN SETTINGS.PY!*
