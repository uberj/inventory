from django.db import models
from django.core.exceptions import ValidationError

from systems.models import System

import mozdns
from core.keyvalue.base_option import DHCPKeyValue
from core.keyvalue.utils import AuxAttr
from core.keyvalue.mixins import KVUrlMixin
from mozdns.address_record.models import BaseAddressRecord
from mozdns.domain.models import Domain
from mozdns.ip.utils import ip_to_dns_form
from mozdns.ptr.models import BasePTR


class StaticReg(BaseAddressRecord, BasePTR, KVUrlMixin):
    # Keep in mind that BaseAddressRecord will have it's methods called before
    # BasePTR
    """
    The StaticReg Class.

        >>> s = StaticReg.objects.create(label=label, domain=domain,
        ... ip_str=ip_str, ip_type=ip_type)

    If you want an A/AAAA, PTR, and a DHCP lease, create on of these objects
    and associate a mac address with it.

    In terms of DNS, a static registration represents a PTR and A record and
    must adhear to the requirements of those classes. StaticReg inherits
    from BaseAddressRecord and will call it's clean and save method. StaticReg
    also inherits from BasePTR and will call :func:`clean_reverse` which
    essentially calls the :class:`PTR` classes :func:`clean` method.


    Using the 'attrs' attribute.

    To interface with the Key Value store of a registration use the 'attrs'
    attribute. This attribute is a direct proxy to the Keys and Values in the
    Key Value store. When you assign an attribute of the 'attrs' attribute a
    value, a key is create/updated. For example:

    >>> sreg = <Assume this is an existing StaticReg instance>
    >>> sreg.update_attrs()  # This updates the object with keys/values already
    >>> # in the KeyValue store.
    >>> sreg.attrs.baz
    '0'

    In the previous line, there was a key called 'baz' and it's value
    would be returned when you accessed the attribute 'baz'.
    >>> sreg.attrs.foo
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'attrs' object has no attribute 'foo'

    Here 'attrs' didn't have an attribute 'foo' which means that there was no
    KeyValue with key 'foo'. If we wanted to create that key and give it a
    value of 'bar' we would do:

    >>> sreg.attrs.bar = 'foo'

    This *immediately* creates a KeyValue pair with key='bar' and value='foo'.

    >>> sreg.attrs.bar = 'baz'

    This *immediately* updates the KeyValue object with a value of 'baz'. It is
    not like the Django ORM where you must call the `save()` function for any
    changes to propagate to the database.
    """
    id = models.AutoField(primary_key=True)
    reverse_domain = models.ForeignKey(
        Domain, null=True, blank=True, related_name="reverse_staticreg_set"
    )

    system = models.ForeignKey(
        System, null=True, blank=True, help_text="System to associate the "
        "registration with"
    )

    attrs = None

    search_fields = ('ip_str', 'fqdn')

    class Meta:
        db_table = 'static_reg'
        unique_together = ('ip_upper', 'ip_lower', 'label', 'domain')

    def __repr__(self):
        return '<StaticReg: {0}>'.format(str(self))

    def __str__(self):
        return "FQDN: {0} IP: {1}".format(self.fqdn, self.ip_str)

    def update_attrs(self):
        self.attrs = AuxAttr(StaticRegKeyValue, self)

    def details(self):
        return (
            ("Name", self.fqdn),
            ("DNS Type", "A/PTR"),
            ("IP", self.ip_str),
        )

    @classmethod
    def get_api_fields(cls):
        return super(StaticReg, cls).get_api_fields()

    @property
    def rdtype(self):
        return 'SREG'

    def record_type(self):
        return 'A/PTR'

    def delete(self, *args, **kwargs):
        if self.reverse_domain and self.reverse_domain.soa:
            self.reverse_domain.soa.schedule_rebuild()
            # The reverse_domain field is in the Ip class.
        super(StaticReg, self).delete(*args, **kwargs)  # BaseAddressRecord

    def save(self, *args, **kwargs):
        urd = kwargs.pop('update_reverse_domain', True)
        self.clean_reverse(update_reverse_domain=urd)  # BasePTR
        super(StaticReg, self).save(*args, **kwargs)
        self.rebuild_reverse()

    def clean(self, validate_glue=True):
        if not self.system:
            raise ValidationError(
                "An registartion means nothing without it's system."
            )
        self.check_A_PTR_collision()
        super(StaticReg, self).clean(  # BaseAddressRecord
            validate_glue=validate_glue, ignore_sreg=True
        )

    def check_A_PTR_collision(self):
        from mozdns.ptr.models import PTR
        from mozdns.address_record.models import AddressRecord

        if PTR.objects.filter(ip_str=self.ip_str, name=self.fqdn).exists():
            raise ValidationError("A PTR already uses this Name and IP")
        if AddressRecord.objects.filter(ip_str=self.ip_str, fqdn=self.fqdn
                                        ).exists():
            raise ValidationError("An A record already uses this Name and IP")

    def check_glue_status(self):
        """
        If this registration is a 'glue' record for a Nameserver instance,
        do not allow modifications to this record. The Nameserver will
        need to point to a different record before this record can
        be updated.
        """
        if self.pk is None:
            return
        # First get this object from the database and compare it to the
        # Nameserver object about to be saved.
        db_self = StaticReg.objects.get(pk=self.pk)
        if db_self.label == self.label and db_self.domain == self.domain:
            return
        # The label of the domain changed. Make sure it's not a glue record
        Nameserver = mozdns.nameserver.models.Nameserver
        if Nameserver.objects.filter(sreg_glue=self).exists():
            raise ValidationError(
                "This registration represents a glue record for a Nameserver. "
                "Change the Nameserver to edit this record."
            )

    A_template = ("{bind_name:$rhs_just} {ttl} {rdclass:$rdclass_just}"
                  "{rdtype_clob:$rdtype_just} {ip_str:$lhs_just}")
    PTR_template = ("{dns_ip:$lhs_just} {ttl} {rdclass:$rdclass_just}"
                    " {rdtype_clob:$rdtype_just} {fqdn:1}.")

    def bind_render_record(self, pk=False, **kwargs):
        self.rdtype_clob = kwargs.pop('rdtype', 'SREG')
        if kwargs.pop('reverse', False):
            self.template = self.PTR_template
            self.dns_ip = ip_to_dns_form(self.ip_str)
        else:
            self.template = self.A_template
        return super(StaticReg, self).bind_render_record(pk=pk, **kwargs)


class StaticRegKeyValue(DHCPKeyValue):
    obj = models.ForeignKey(
        StaticReg, related_name='keyvalue_set', null=False
    )

    class Meta:
        db_table = 'static_reg_key_value'
        unique_together = ('key', 'value', 'obj')
