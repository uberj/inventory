from django.core.exceptions import ValidationError

from core.interface.bonded_intr import BondedInterface

def coerce_to_bonded(intr):
    """
    Coerce a non bonded StaticInterface into a bonded Interface.
    :param intr:
    :type intr: :class:`StaticInterface`
    :returns: (:class:`StaticInterface, :class:`BondedInterface`)
    :raises: ValidationError

    If there are errors errors a ValidationError will be raised with a message
    the should be shown to the user.
    """
    if intr.bondedintr_set.all().exists():
        raise ValidationError("This interface is already a bonded interface")

    bi = BondedInterface(
        mac=intr.mac, interface_name=intr.interface_name, intr=intr
    )
    bi.clean()
    bi.save()

    intr.mac = 'virtual'
    intr.interface_name = intr.system.get_next_bond_name()
    return intr, bi
