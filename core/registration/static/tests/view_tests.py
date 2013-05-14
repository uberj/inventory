from django.test import TestCase, TestClient
from django.core.exceptions import ValidationError

from core.registration.static.models import StaticReg
from systems.models import System
from mozdns.domain.models import Domain
from mozdns.view.models import View
from mozdns.tests.utils import create_fake_zone


class StaticRegViewTests(TestCase):
    def setUp(self):
        View.objects.create(name="private")
        View.objects.create(name="public")
        self.d = create_fake_zone('mozilla.com', suffix="")
        self.rd = create_fake_zone('10.in-addr.arpa', suffix="")

    def test_create_with_no_hwadapters(self):
        pass

    def test_create_with_hwadapters(self):
        pass

    def test_create_invalid_sreg(self):
        pass

    def test_create_invalid_hwadapter(self):
        pass
