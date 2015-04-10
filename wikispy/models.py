from django.db import models

class Edit(models.Model):
    wikipedia_id = models.IntegerField()
    title = models.CharField(max_length=1024)
    ip = models.GenericIPAddressField()
    wiki = models.ForeignKey('Wiki')

class Wiki(models.Model):
    name = models.CharField(max_length=1024)
