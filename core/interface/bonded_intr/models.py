from django.db import models
from django.core.exceptions import ValidationError

from core.keyvalue.models import KeyValue
from core.keyvalue.utils import AuxAttr
from core.validation import validate_mac, validate_bonded_intr_name
from core.interface.static_intr.models import StaticInterface


class BondedInterface(models.Model):
    """
    The BondedInterface Class.

        >>> bi = BondedInterface(intr=intr, mac=mac)
        >>> bi.full_clean()
        >>> bi.save()
    """

    id = models.AutoField(primary_key=True)
    mac = models.CharField(max_length=17, validators=[validate_mac],
                           help_text="Mac address in format XX:XX:XX:XX:XX:XX")
    interface_name = models.CharField(
        max_length=255, validators=[validate_bonded_intr_name]
    )
    intr = models.ForeignKey(
        StaticInterface, null=True, blank=True, related_name='bondedintr_set'
    )
    search_fields = ("mac", "interface_name", "intr__fqdn")

    def update_attrs(self):
        self.attrs = AuxAttr(BondedIntrKeyValue, self)

    def details(self):
        return (
            ("mac", self.mac),
            ("Interface id", self.interface_name),
        )

    class Meta:
        db_table = "bonded_interface"
        unique_together = ("mac", "intr", "interface_name")

    @classmethod
    def get_api_fields(cls):
        return ['mac', 'intr', 'interface_name']

    def get_edit_url(self):
        return "/core/interface/{0}/update/".format(self.pk)

    def get_delete_url(self):
        return "/core/interface/{0}/delete/".format(self.pk)

    def get_absolute_url(self):
        return "/systems/show/{0}/".format(self.system.pk)


    def clean(self, *args, **kwargs):
        self.mac = self.mac.lower()

    def __repr__(self):
        return "<BondedInterface: {0}>".format(str(self))

    def __str__(self):
        # return "IP:{0} Full interface_name:{1} Mac:{2}".format(self.ip_str,
        #        self.fqdn, self.mac)
        return "IP:{0} Full interface_name:{1}".format(self.mac,
                                             self.interface_name)


class BondedIntrKeyValue(KeyValue):
    obj = models.ForeignKey(
        BondedInterface, related_name='keyvalue_set', null=False
    )

    class Meta:
        db_table = "bonded_inter_key_value"
        unique_together = ("key", "value", "obj")

    def _aa_domain_name_servers(self):
        """DHCP option domain-name-servers
        """
        if not self.value:
            raise ValidationError("Domain Name Servers Required")

    def _aa_domain_name(self):
        """DHCP option domain-name
        """
        if not self.value:
            raise ValidationError("Domain Name Required")

    def _aa_filename(self):
        """DHCP option filename
        """
        if not self.value:
            raise ValidationError("Filename Required")
