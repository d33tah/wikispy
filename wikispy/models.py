from django.db import models

class RightAnchored(models.Lookup):
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
    #ip = models.GenericIPAddressField()
    wiki = models.ForeignKey('Wiki')
    rdns = models.ForeignKey('RDNS', db_column='ip')

class RDNS(models.Model):
    class Meta:
        db_table = 'rdns'
    ip = models.GenericIPAddressField(primary_key=True)
    rdns = models.CharField(max_length=253)

class Wiki(models.Model):
    name = models.CharField(max_length=1024)
