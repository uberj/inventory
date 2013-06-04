from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import ObjectUrlMixin, CoreDisplayMixin
from core.keyvalue.models import KeyValue
from core.utils import networks_to_Q, to_a
from core.validation import validate_site_name


class Site(models.Model, ObjectUrlMixin, CoreDisplayMixin):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(
        max_length=255, null=True, blank=True
    )
    name = models.CharField(max_length=255, validators=[validate_site_name])
    parent = models.ForeignKey("self", null=True, blank=True)

    search_fields = ('full_name',)

    template = (
        "{full_name:$lhs_just} {rdtype:$rdtype_just} name: {name:$rhs_just}"
    )

    class Meta:
        db_table = 'site'
        unique_together = ('name', 'parent')

    def __str__(self):
        return "{0}".format(self.full_name)

    def __repr__(self):
        return "<Site {0}>".format(str(self))

    @classmethod
    def get_api_fields(cls):
        return ['name', 'parent', 'full_name']

    @property
    def rdtype(self):
        return 'SITE'

    def save(self, *args, **kwargs):
        self.full_clean()
        self.full_name = self.get_site_path()
        super(Site, self).save(*args, **kwargs)

    def clean(self):
        if self.pk:
            db_self = self.__class__.objects.get(pk=self.pk)
            if self.site_set.exists() and self.name != db_self.name:
                raise ValidationError(
                    "This site has child sites. You cannot change it's name "
                    "without affecting all child sites."
                )

    def details(self):
        details = [
            ('Name', self.full_name),
        ]
        if self.parent:
            details.append(
                ('Parent Site', to_a(self.parent.full_name, self.parent))
            )
        return details

    def get_site_path(self):
        target = self
        npath = [self.name]
        while True:
            if target.parent is None:
                break
            else:
                npath.append(target.parent.name)
                target = target.parent
        return '.'.join(npath)

    def compile_Q(self):
        """Compile a Django Q that will match any IP inside this site."""
        return networks_to_Q(self.network_set.all())


class SiteKeyValue(KeyValue):
    obj = models.ForeignKey(Site, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = 'site_key_value'
        unique_together = ('key', 'value')

    def _aa_address(self):
        """
        The address of this site.
        """
        return

    def _aa_description(self):
        """
        A description of this site.
        """
        return

    def _aa_type(self):
        """
        The type of this site. Valid types include: DC, BU, AWS, and Office.
        """
        valid_site_types = ['dc', 'bu', 'office', 'aws']
        if self.value.lower() not in valid_site_types:
            raise ValidationError(
                "{0} not a valid site type".format(self.value)
            )
        if self.value.lower() == 'office':
            self.value = self.value.lower().title()
        else:
            self.value = self.value.upper()
