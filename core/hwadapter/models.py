from django.db import models
from django.core.exceptions import ValidationError

from core.group.models import Group
from core.keyvalue.base_option import DHCPKeyValue, CommonOption
from core.mixins import ObjectUrlMixin
from core.registration.static_reg.models import StaticReg
from core.validation import validate_mac


class HardwareAdapter(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, null=False, default='')
    mac = models.CharField(
        max_length=17, validators=[validate_mac],
        help_text="Mac address in format XX:XX:XX:XX:XX:XX"
    )
    group = models.ForeignKey(Group, null=True, blank=True)
    sreg = models.ForeignKey(
        StaticReg, null=True, blank=True, related_name='hwadapter_set'
    )

    search_fields = ('mac', 'group__name', 'sreg__ip_str', 'sreg__fqdn')

    class Meta:
        db_table = 'hwadapter'
        unique_together = ('mac', 'sreg',)

    def __str__(self):
        return '{0}'.format(self.mac)

    def __repr__(self):
        return '<HWAdapter: {0}>'.format(self)

    @classmethod
    def get_api_fields(cls):
        return ['mac', 'name', 'description']

    def save(self, *args, **kwargs):
        if not self.sreg:
            raise ValidationError(
                "Hardware Adapters need to be associated with a static IP "
                "registration"
            )
        super(HardwareAdapter, self).save(*args, **kwargs)


class HardwareAdapterKV(DHCPKeyValue, CommonOption):
    obj = models.ForeignKey(
        HardwareAdapter, related_name='keyvalue_set', null=False
    )

    class Meta:
        db_table = 'hwadapter_key_value'
        unique_together = ('key', 'value')
