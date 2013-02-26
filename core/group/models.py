from django.db import models

from core.mixins import ObjectUrlMixin

from core.keyvalue.models import KeyValue


class Group(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def details(self):
        return (
            ("Name", self.name),
        )

    class Meta:
        db_table = "group"
        unique_together = ("name",)

    def __str__(self):
        return "{0} {1}".format(self.name)

    def __repr__(self):
        return "<Vlan {0}>".format(str(self))


class GroupKeyValue(KeyValue):
    obj = models.ForeignKey(Group, related_name='keyvalue_set', null=False)

    class Meta:
        db_table = "group_key_value"
        unique_together = ("key", "value")

    def _aa_description(self):
        return
