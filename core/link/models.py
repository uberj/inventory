from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import ObjectUrlMixin, CoreDisplayMixin
from core.keyvalue.models import KeyValue
from core.site.models import Site
#from core.vendor.models import Vendor
from core.utils import to_a
from core.network.models import Network

"""
Many networks can associate with the same link. A link can associate itself
with one network. A Link is a logical construct and has no physical basis.
Circuits, which are physical entities offered by providers, comprise a link.


                             +--------------+
                             |  Network X   |
                             |--------------+
                             |  10.2.2.0/21 |
                             +-------^------+
       +--------------+              |             +--------------+
       |  Network a   |              |             |  Network c   |
       |--------------+---+          |          +--+--------------|
       |  10.2.2.0/21 |   |          |          |  |  10.9.2.0/24 |
       +--------------+   |  +-------+-------+  |  +--------------+
              .           +-->   Link A      <--+         .
              .              |---------------|            .
              .           +-->               <--+         .
       +--------------+   |  +----^----^-----+  |  +--------------+
       |  Network b   |   |       |    |        |  |  Network d   |
       |--------------+---+       |    |        +--+--------------|
       |  10.2.5.0/24 |           |    |           |  10.9.4.0/21 |
       +--------------+           |    |           +--------------+
                        +---------+    +-------+
                        |                      |
                        |                      |
                  +-----+-----+         +------+-----+
                  | Circuit 2 |         |  Circuit 1 |
                  |-----------|         |------------|
                  |           |         |            |
                  |           |         |            |
                  |           | . . . . |            |
                  |           |         |            |
                  |           |         |            |
                  +-----------+         +------------+

"""


class Link(models.Model, ObjectUrlMixin, CoreDisplayMixin):
    network = models.ForeignKey(
        Network, null=True, blank=True, on_delete=models.SET_NULL
    )
    a_site = models.ForeignKey(
        Site, null=False, blank=False, related_name='a_circuit_set'
    )
    z_site = models.ForeignKey(
        Site, null=False, blank=False, related_name='z_circuit_set'
    )
    search_fields = (
        'a_site__name',
        'z_site__name',
        'network__network_str'
    )

    template = (
        "{full_name:$lhs_just} {rdtype:$rdtype_just} {full_name:$rhs_just}"
    )

    class Meta:
        db_table = 'link'
        unique_together = ('a_site', 'z_site', 'network')

    def __str__(self):
        return "{0} to {1} {2}".format(
            self.a_site.name, self.z_site.name,
            "via {0}".format(self.network) if self.network else "(No Network)"
        )

    def __repr__(self):
        return "<LINK {0}>".format(self)

    @property
    def rdtype(self):
        return 'LINK'

    def save(self, *args, **kwargs):
        if self.a_site == self.z_site:
            raise ValidationError(
                "Cannot assign A end and Z end to be the same site"
            )
        super(Link, self).save(*args, **kwargs)

    def details(self):
        return (
            ('network', self.network),
            ('A End', to_a(self.a_site.full_name, self.a_site)),
            ('Z End', to_a(self.z_site.full_name, self.z_site)),
        )


class LinkKeyValue(KeyValue):
    obj = models.ForeignKey(Link, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = 'link_key_value'
        unique_together = ('key', 'value', 'obj')
