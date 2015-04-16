from django.db import models

from django.db import connection
import json


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
    wikipedia_id = models.IntegerField()
    title = models.CharField(max_length=1024)
    wiki = models.ForeignKey('Wiki')
    rdns = models.ForeignKey('RDNS', db_column='ip')


class RDNS(models.Model):
    class Meta:
        db_table = 'rdns'
    # FIXME: This is not actually a primary key yet, but this walkaround worked
    # well so far.
    ip = models.GenericIPAddressField(primary_key=True)
    rdns = models.CharField(max_length=253)


class Wiki(models.Model):
    name = models.CharField(max_length=1024)


def plan_scans_table(d, t):
    """
    Recursively looks for any Plan nodes that suggest that a seq scan would be
    performed. Returns True if such node was found.
    """
    if isinstance(d, list) or isinstance(d, tuple):
        if len(d) == 1:
            return plan_scans_table(d[0], t)
        else:
            raise NotImplementedError("List has more than one item")
    elif isinstance(d, dict):
        if 'Plans' in d:
            if isinstance(d['Plans'], list):
                for x in d['Plans']:
                    if plan_scans_table(x, t):
                        return True
        elif 'Plan' in d:
            return plan_scans_table(d['Plan'], t)
        elif 'Node Type' in d and 'Relation Name' in d:
            return d['Node Type'] == 'Seq Scan' and d['Relation Name'] == t
        else:
            raise NotImplementedError("d has no Plans, lan or Node Type")
    else:
        raise NotImplementedError("Unknown type of d")
    return False


def query_scans_table(query, table):
    """
    Tests if the given query would perform a full sequential scan on a given
    table. Only works with PostgreSQL.
    """
    # simple str(query) wouldn't do - PostgreSQL driver mishandles quoting.
    sql, params = query.sql_with_params()
    cursor = connection.cursor()
    sql = "EXPLAIN (format JSON)" + sql
    cursor.execute(sql, params)
    d = cursor.fetchall()
    # Django's cursor doesn't automatically decode JSON objects, so let's check
    # for that and fix it if necessary.
    if len(d) == 1 and len(d[0]) == 1 and isinstance(d[0][0], str):
        d = json.loads(d[0][0])
    return plan_scans_table(d, table)
