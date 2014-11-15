from django.db import models

"""
A note about these "Zeus" objects. Inventory is *not* authoritative for this
information. All zeus information is brought into Inventory from an external
source that does its own type/data checks.

These ORM models are to be a lightweight index tree that can be searched
quickly and be updated quickly. An update is usually composed of deleting
everything and then re-adding everything (in one db transaction). Foreign keys
would only slow this process down so they are not used.
"""


class Node(models.Model):
    node_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    pool = models.CharField(max_length=255, null=True)


class VServer(models.Model):
    name = models.CharField(max_length=255, null=True)
    pool = models.CharField(max_length=255, null=True)


class VServerListenOnTig(models.Model):
    vserver = models.CharField(max_length=255, null=True)
    tig = models.CharField(max_length=255, null=True)


class TIG(models.Model):
    name = models.CharField(max_length=255, null=True)


class Pool(models.Model):
    name = models.CharField(max_length=255, null=True)
