from django.db import models

from core.mixins import ObjectUrlMixin, CoreDisplayMixin
from core.keyvalue.models import KeyValue
from core.link.models import Link
from core.circuit.constants import SERVICE_TYPE


class Circuit(models.Model, ObjectUrlMixin, CoreDisplayMixin):
    id = models.AutoField(primary_key=True)

    # Relational fields
    links = models.ManyToManyField(Link)
    #vendor = models.ForeignKey(Vendor, null=True, blank=True)

    # Non-relational fields (Meta Data)
    # circuit_id is not the database ID (above). Its the id that netops is
    # calling a circuit id and is assigned by the vendor.
    circuit_id = models.CharField(max_length=255, null=False, blank=False)
    service = models.CharField(
        max_length=3, choices=SERVICE_TYPE, default='N/A'
    )
    service_order_number = models.CharField(
        max_length=255, default='N/A', validators=[]
    )
    bandwidth = models.CharField(
        max_length=255, default='N/A', validators=[]
    )
    port_size = models.CharField(
        max_length=255, default='N/A', validators=[]
    )
    price = models.CharField(
        max_length=255, default='N/A', validators=[]
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
        return "ID: {0}".format(self.circuit_id)

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
            ('Service', self.service),
            ('Bandwidth', self.bandwidth),
            ('Port Size', self.port_size),
        )
        return details


class CircuitKeyValue(KeyValue):
    obj = models.ForeignKey(Circuit, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = 'circuit_key_value'
        unique_together = ('key', 'value', 'obj')
