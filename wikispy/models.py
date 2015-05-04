from django.db import models

from django.db import connection
import json
from django.utils.translation import ugettext as _


class RightAnchored(models.Lookup):
    """
    This lookup was created in order to enable queries like:

    SELECT * FROM rdns WHERE REVERSE(rdns) LIKE REVERSE('%.gov.pl%")

    This was because I picked an index that forced me to call queries like
    this.
    """
    lookup_name = 'rightanchored'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'REVERSE(%s) LIKE REVERSE(%s)' % (lhs, rhs), params

models.CharField.register_lookup(RightAnchored)


class Edit(models.Model):
    wikipedia_edit_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=1024)
    wiki = models.ForeignKey('Wiki')
    ip = models.GenericIPAddressField(db_index=True)
    time = models.DateTimeField()
    view_count = models.IntegerField(default=0)
    rdns = models.CharField(max_length=253)


class Wiki(models.Model):
    name = models.CharField(max_length=1024)
    # The longest I found is zh-classical which is 12 letters long, but it
    # won't hurt to store some more. The longest domain I found was
    # wikimediafoundation.org which hosted all languages under a single
    # language (articles split by categories), but still - I'll leave some room
    # just in case.
    language = models.CharField(max_length=32)
    domain = models.CharField(max_length=64)

class ViewRecord(models.Model):
    ip = models.GenericIPAddressField(db_index=True)
    wikipedia_edit_id = models.IntegerField()
    wiki = models.ForeignKey('Wiki')


def plan_scans_table(d, table):
    """
    Recursively looks for any Plan nodes that suggest that a seq scan would be
    performed. Returns True if such node was found. This is ugly because I was
    too lazy to check how the data structure looked like and I basically coded
    it based on one example.

    Args:
      d (dict/list/tuple): the dictionary to be parsed
      table (str): string that shouldn't be scanned sequentially

    Returns bool
    """
    if isinstance(d, list) or isinstance(d, tuple):
        if len(d) == 1:
            return plan_scans_table(d[0], table)
        else:
            raise NotImplementedError("List has more than one item")
    elif isinstance(d, dict):
        if 'Plans' in d:
            if isinstance(d['Plans'], list):
                for x in d['Plans']:
                    if plan_scans_table(x, table):
                        return True
        elif 'Plan' in d:
            return plan_scans_table(d['Plan'], table)
        elif 'Node Type' in d and 'Relation Name' in d:
            return d['Node Type'] == 'Seq Scan' and d['Relation Name'] == table
        else:
            if d.get('Node Type') == 'Bitmap Index Scan':
                return False
            raise NotImplementedError("d has no Plans, Plan or Node Type")
    else:
        raise NotImplementedError("Unknown type of d")
    return False

def sql_scans_table(sql, table, params=None):
    """
    Tests if the given SQL query would perform a full sequential scan on a
    given table. Only works with PostgreSQL.

    Args:
      query (django.db.models.query.QuerySet): the query that will be checked
      table (str): string that shouldn't be scanned sequentially

    Returns bool
    """
    cursor = connection.cursor()
    sql = "EXPLAIN (format JSON)" + sql
    if params is not None:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    d = cursor.fetchall()
    # Django's cursor doesn't automatically decode JSON objects, so let's check
    # for that and fix it if necessary.
    if len(d) == 1 and len(d[0]) == 1 and isinstance(d[0][0], str):
        d = json.loads(d[0][0])
    return plan_scans_table(d, table)

def query_scans_table(query, table):
    """
    Tests if the given query would perform a full sequential scan on a given
    table. Only works with PostgreSQL.

    Args:
      query (django.db.models.query.QuerySet): the query that will be checked
      table (str): string that shouldn't be scanned sequentially

    Returns bool
    """
    # simple str(query) wouldn't do - PostgreSQL driver mishandles quoting.
    sql, params = query.sql_with_params()
    return sql_scans_table(sql, table, params)

def get_edits(wikiname, offset=0, limit=50, random=False, rdns=None,
              startip=None, endip=None, wikipedia_edit_id=None):
    cursor = connection.cursor()
    cursor.execute("SET enable_seqscan=off;")

    order_sql = ('\nORDER BY "wikispy_edit"."view_count" DESC,'
                 ' "wikispy_edit"."title" ASC')
    limit_sql = ""
    offset_sql = ""
    if not random:
        if limit != 0:
            limit_sql = "\nLIMIT %s" % int(limit + 1)
        offset_sql = "\nOFFSET %s" % int(offset)
    else:
        order_sql = '\nORDER BY random()'
        limit_sql = '\nLIMIT 1'
    if rdns is not None:
        where_sql = 'REVERSE("wikispy_edit"."rdns") LIKE REVERSE(%s)'
        params = ['%' + rdns, wikiname]
    elif startip is not None and endip is not None:
        where_sql = '"wikispy_edit"."ip" >= %s and "wikispy_edit"."ip" <= %s'
        params = [startip, endip, wikiname]
    elif wikipedia_edit_id is not None:
        where_sql = '"wikispy_edit"."wikipedia_edit_id" = %s'
        params = [wikipedia_edit_id, wikiname]

    sql = """
    SELECT  "wikispy_edit"."id",
            "wikispy_edit"."wikipedia_edit_id",
            "wikispy_edit"."title",
            "wikispy_edit"."ip",
            "wikispy_edit"."wiki_id",
            "wikispy_edit"."time",
            "wikispy_edit"."view_count",
            "wikispy_edit"."rdns",
            "wikispy_wiki"."language",
            "wikispy_wiki"."domain"
    FROM "wikispy_edit"
    INNER JOIN "wikispy_wiki"
        ON ( "wikispy_edit"."wiki_id" = "wikispy_wiki"."id" )
    WHERE
    """ + where_sql + """
        AND
            "wikispy_wiki"."name" = %s
    """ + order_sql + limit_sql + offset_sql

    if sql_scans_table(sql, 'wikispy_edit', params):
        raise ValueError("The query is too big.")
    #if sql_scans_table(sql, "wikispy_edit", params):
    #    raise RuntimeError("The query is too big.")
    # http://stackoverflow.com/a/2679222/1091116
    cursor.execute(sql, params)
    description = [x[0] for x in cursor.description]
    for row in cursor:
        yielded = dict(zip(description, row))
        yield yielded

def mark_watched(ip, wiki, wikipedia_edit_id):
    vq = ViewRecord.objects.filter(ip=ip, wiki__id=wiki.id,
                                   wikipedia_edit_id=wikipedia_edit_id)
    if len(vq) != 0:
        return
    wq = Edit.objects.filter(wiki__id=wiki.id,
                             wikipedia_edit_id=wikipedia_edit_id)
    if len(wq) != 1:
        raise ValueError(_("No edit found matching the query."))
    v = ViewRecord()
    v.ip = ip
    v.wikipedia_edit_id = wikipedia_edit_id
    v.wiki = wiki
    v.save()
    wq[0].view_count += 1
    wq[0].save()
