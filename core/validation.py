from django.core.exceptions import ValidationError
import re


mac_match = "^[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:"\
    "[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]$"
is_mac = re.compile(mac_match)


def validate_mac(mac):
    mac = mac.lower()
    if not isinstance(mac, basestring):
        raise ValidationError("Mac Address not of valid type.")

    # TODO, I'm drunk. Write a better regex
    if not is_mac.match(mac):
        raise ValidationError("Mac Address not in valid format.")

valid_name_formats = [
    re.compile("^eth\d+$"),
    re.compile("^nic\d+$"),
    re.compile("^mgmt\d+$")
]

def validate_bonded_intr_name(name):
    # TODO ^ fix that regex, he was drunk.
    for f in valid_name_formats:
        if f.match(name):
            return
    raise ValidationError(
        "Not in valid format. Try something like eth0 or eth1."
    )

def validate_intr_name(name):
    if name.lower() != 'virtual':
        validate_bonded_intr_name(name)

