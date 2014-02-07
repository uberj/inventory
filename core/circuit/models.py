from django.db import models

from core.mixins import ObjectUrlMixin, CoreDisplayMixin
from core.keyvalue.models import KeyValue
from core.site.models import Site
#from core.vendor.models import Vendor
from core.network.models import Network
from core.circuit.constants import SERVICE_TYPE
from core.circuit.validation import (
    validate_no_spaces, validate_link_capacity
)

from core.validation import validate_price


class Circuit(models.Model, ObjectUrlMixin, CoreDisplayMixin):
    id = models.AutoField(primary_key=True)

    # Relational fields
    a_site = models.ForeignKey(
        Site, null=False, blank=False, related_name='a_circuit_set'
    )
    z_site = models.ForeignKey(
        Site, null=False, blank=False, related_name='z_circuit_set'
    )
    network = models.ForeignKey(Network, null=True, blank=True)
    #vendor = models.ForeignKey(Vendor, null=True, blank=True)

    # Non-relational fields (Meta Data)
    # circuit_id is not the database ID (above). Its the id that netops is
    # calling a circuit id and is assigned by the vendor.
    circuit_id = models.CharField(max_length=255, null=False, blank=False)
    service = models.CharField(
        max_length=255, choices=SERVICE_TYPE, default='N/A'
    )
    service_order_numer = models.CharField(
        max_length=255, default='N/A', validators=[validate_no_spaces]
    )
    bandwidth = models.CharField(
        max_length=255, default='N/A', validators=[validate_link_capacity]
    )
    port_size = models.CharField(
        max_length=255, default='N/A', validators=[validate_link_capacity]
    )
    price = models.CharField(
        max_length=255, default='N/A', validators=[validate_price]
    )

    expiration_date = models.DateField(blank=False, null=False)
    purchase_date = models.DateField(blank=False, null=False)

    search_fields = (
        'circuit_id', 'a_site__name', 'z_site__name',
        'network__network_str'
    )

    template = (
        "{full_name:$lhs_just} {rdtype:$rdtype_just} {full_name:$rhs_just}"
    )

    class Meta:
        db_table = 'circuit'
        unique_together = ('circuit_id',)

    def __str__(self):
        return "{0} from {1} to {2} {3}".format(
            self.circuit_id, self.a_site.name, self.z_site.name,
            "via {0}".format(self.network) if self.network else "(No Network)"
        )

    def __repr__(self):
        return "<Circuit {0}>".format(self)

    @property
    def rdtype(self):
        return 'CIRCUIT'

    def save(self, *args, **kwargs):
        super(Circuit, self).save(*args, **kwargs)

    def clean(self):
        pass

    def details(self):
        details = (
            ('ID', self.circuit_id),
            ('A End', self.a_site),
            ('Z End', self.z_site),
            ('Network', self.network if self.network else 'No Network'),
        )
        return details


class CircuitKeyValue(KeyValue):
    obj = models.ForeignKey(Circuit, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = 'circuit_key_value'
        unique_together = ('key', 'value', 'obj')
