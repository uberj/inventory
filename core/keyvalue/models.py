from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError


class KeyValue(models.Model):
    """How this KeyValue class works:
        The KeyValue objects have functions that correspond to different
        keys. When a key is saved an attempt is made to find a validation
        function for that key.

        >>> attr = hasattr(kv, key)

        If `attr` is not None, then it is checked for callability.

        >>> attr = getattr(kv, key)
        >>> callable(attr)

        If it is callable, it is called with the value of the key.

        >>> kv.attr(kv.value)

        The validator is then free to raise exceptions if the value being
        inserted is invalid.

        When a validator for a key is not found, the KeyValue class can either
        riase an exception or not. This behavior is controled by the
        'force_validation' attribute: if 'force_validation' is 'True' and
        KeyValue requires a validation function. The 'require_validation' param
        to the clean method can be used to override the behavior of
        'force_validation'.

        Subclass this class and include a Foreign Key when needed.

        Validation functions can start with '_aa_'. 'aa' stands for auxililary
        attribute.
    """
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    force_validation = False

    class Meta:
        abstract = True

    def __repr__(self):
        return "<{0}>".format(self)

    def __str__(self):
        return "Key: {0} Value {1}".format(self.key, self.value)

    @property
    def uri(self):
        return '/en-US/core/keyvalue/api/{0}/{1}/update/'.format(
            self.__class__.__name__.lower(), self.pk
        )

    def get_absolute_url(self):
        return '/en-US/core/keyvalue/{0}/{1}/'.format(
            self.__class__.__name__.lower(), self.obj.pk
        )

    def get_bundle(self):
        return {
            'key': self.key, 'value': self.value, 'uri': self.uri,
            'kv_pk': self.pk, 'obj_pk': self.obj.pk
        }

    def clean(self, require_validation=True, check_unique=True):
        key_attr = self.key.replace('-', '_')
        # aa stands for auxilarary attribute.
        if (not hasattr(self, key_attr) and
                not hasattr(self, "_aa_" + key_attr)):
            # ??? Do we want this?
            if self.force_validation and require_validation:
                raise ValidationError("No validator for key %s" % self.key)
            else:
                if check_unique:  # Since we aren't call this later
                    self.validate_unique()
                return
        if hasattr(self, key_attr):
            validate = getattr(self, key_attr)
        else:
            validate = getattr(self, "_aa_" + key_attr)

        if not callable(validate):
            raise ValidationError("No validator for key %s not callable" %
                                  key_attr)
        try:
            validate()
        except TypeError, e:
            # We want to catch when the validator didn't accept the correct
            # number of arguements.
            raise ValidationError("%s" % str(e))
        if check_unique:
            self.validate_unique()

    def validate_unique(self):
        if (self.__class__.objects.filter(
                key=self.key, value=self.value, obj=self.obj).
                filter(~Q(id=self.pk)).exists()):
            raise ValidationError("A key with this value already exists.")
