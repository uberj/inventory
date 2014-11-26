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
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def snippets(self):
        pools = self.pools
        for pool in pools:
            for vserver in pool.vservers:
                tigs = map(lambda t: t.url(), vserver.tigs)
                yield (
                    "{node_id} is in pool '{pool}'. That pool is backing the "
                    "tigs {tigs} and is configured via the {vserver} vserver"
                ).format(
                    tigs=', '.join(tigs),
                    vserver=vserver.name,
                    pool=pool.name,
                    node_id=self.node_id
                )

    @property
    def pools(self):
        return Pool.objects.filter(name=self.pool)


class VServer(models.Model):
    name = models.CharField(max_length=255, null=True)
    pool = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def tigs(self):
        rels = VServerListenOnTig.objects.filter(vserver=self.name)

        def get_tig(rel):
            try:
                return TIG.objects.get(name=rel.tig)
            except TIG.DoesNotExist:
                return False

        return filter(None, map(get_tig, rels))


class VServerListenOnTig(models.Model):
    vserver = models.CharField(max_length=255, null=True)
    tig = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)


class TIG(models.Model):
    name = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    def url(self):
        return "<a href=''>{0}</a>".format(self.name)


class Pool(models.Model):
    name = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def vservers(self):
        return VServer.objects.filter(pool=self.name)


class ZXTM(models.Model):
    name = models.CharField(max_length=255, null=True)
