from django.db import models
from os import path

"""
A note about these "Zeus" objects. Inventory is *not* authoritative for this
information. All zeus information is brought into Inventory from an external
source that does its own type/data checks.

These ORM models are to be a lightweight index tree that can be searched
quickly and be updated quickly. An update is usually composed of deleting
everything and then re-adding everything (in one db transaction). Foreign keys
would only slow this process down so they are not used.
"""


class ZXTMMixin(object):
    def get_zxtm(self):
        try:
            return ZXTM.objects.get(name=self.zxtm)
        except ZXTM.DoesNotExist:
            return None
        return "<a href='{0}'>{0}</a>".format(self.name)


class Node(ZXTMMixin, models.Model):
    node_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    pool = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def snippets(self):
        pools = self.pools
        zxtm = self.get_zxtm()
        if not zxtm:
            zxtm_a = "No ZXTM"
        else:
            zxtm_a = zxtm.a

        for pool in pools:
            for vserver in pool.vservers:
                tigs = map(lambda t: t.a, vserver.tigs)
                if len(tigs) > 1:
                    s = 's'
                else:
                    s = ''
                yield (
                    "[{zxtm}] {node_id} is in pool {pool}. That pool is "
                    "backing the tig{s} {tigs} and is configured via the "
                    "{vserver} vserver"
                ).format(
                    zxtm=zxtm_a,
                    tigs=', '.join(tigs),
                    s=s,
                    vserver=vserver.a,
                    pool=pool.a,
                    node_id=self.node_id
                )

    @property
    def pools(self):
        return Pool.objects.filter(name=self.pool, zxtm=self.zxtm)


class VServer(ZXTMMixin, models.Model):
    name = models.CharField(max_length=255, null=True)
    pool = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def tigs(self):
        rels = VServerListenOnTig.objects.filter(
            vserver=self.name, zxtm=self.zxtm
        )

        def get_tig(rel):
            try:
                return TIG.objects.get(name=rel.tig)
            except TIG.DoesNotExist:
                return False

        return filter(None, map(get_tig, rels))

    @property
    def url(self):
        return path.join(
            self.get_zxtm().url,
            "apps/zxtm/?name={0}&section=Virtual%20Servers%3AEdit".format(
                self.name)
        )

    @property
    def a(self):
        return "<a href='{0}'>{1}</a>".format(self.url, self.name)


class VServerListenOnTig(ZXTMMixin, models.Model):
    vserver = models.CharField(max_length=255, null=True)
    tig = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)


class TIG(ZXTMMixin, models.Model):
    name = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def url(self):
        return path.join(
            self.get_zxtm().url,
            "apps/zxtm/index.fcgi?name={0}&section=Traffic%20IP%20Groups%3AEdit".format(self.name)  # noqa
        )

    @property
    def a(self):
        return "<a href='{0}'>{1}</a>".format(self.url, self.name)


class Pool(ZXTMMixin, models.Model):
    name = models.CharField(max_length=255, null=True)
    zxtm = models.CharField(max_length=255, null=True)

    @property
    def vservers(self):
        return VServer.objects.filter(pool=self.name, zxtm=self.zxtm)

    @property
    def url(self):
        return path.join(
            self.get_zxtm().url,
            "apps/zxtm/?name={0}&section=Pools%3AEdit".format(self.name)
        )

    @property
    def a(self):
        return "<a href='{0}'>{1}</a>".format(self.url, self.name)


class ZXTM(models.Model):
    name = models.CharField(max_length=255, null=True)

    @property
    def url(self):
        return self.name

    @property
    def a(self):
        return "<a href='{0}'>{1}</a>".format(self.url, self.name)
