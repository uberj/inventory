from django.test import TestCase

from core.interface.bonded_intr.models import BondedInterface
from core.interface.utils import coerce_to_bonded
from core.interface.static_intr.models import StaticInterface
from systems.models import System

from mozdns.tests.utils import create_fake_zone


class BondedInterTests(TestCase):
    def setUp(self):
        self.domain = create_fake_zone("bonded.scl2.mozilla.com", suffix="")
        self.rdomain = create_fake_zone("10.in-addr.arpa", suffix="")
        self.system = System(hostname="asdf.adfk.mozilla.com")
        self.system.save()

    def test_coerce1(self):
        interface_name = 'eth1'
        intr = StaticInterface(label='adsf', domain=self.domain,
                mac="00:11:22:33:44:55", ip_str="10.0.2.2",
                interface_name=interface_name, system=self.system)
        intr.clean()
        intr.save()

        intr, bi, errors = coerce_to_bonded(intr)
        self.assertFalse(errors)
        self.assertEqual(intr.mac, 'virtual')
        self.assertEqual(intr.interface_name, 'bond0')
        self.assertEqual(bi.interface_name, interface_name)
        self.assertEqual(intr.bondedintr_set.all().count(), 1)

    def test_coerce2(self):
        interface_name = 'eth2'
        intr = StaticInterface(label='adsf', domain=self.domain,
                mac="00:11:22:33:44:55", ip_str="10.0.2.2",
                interface_name=interface_name, system=self.system)
        intr.clean()
        intr.save()

        intr, bi, errors = coerce_to_bonded(intr)
        self.assertFalse(errors)
        self.assertEqual(intr.mac, 'virtual')
        self.assertEqual(intr.interface_name, 'bond0')
        self.assertEqual(bi.interface_name, interface_name)
        self.assertEqual(intr.bondedintr_set.all().count(), 1)

        bi2 = BondedInterface(mac="00:11:22:33:44:66", intr=intr,
                interface_name="eth9")
        bi2.clean()
        bi2.save()

        self.assertEqual(intr.bondedintr_set.all().count(), 2)
