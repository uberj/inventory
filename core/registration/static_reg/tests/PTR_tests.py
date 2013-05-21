from django.test import TestCase
from django.core.exceptions import ValidationError

from core.registration.static_reg.models import StaticReg
from systems.models import System
from mozdns.domain.models import Domain
from mozdns.ptr.models import PTR

from mozdns.ip.utils import ip_to_domain_name


class PTRStaticRegTests(TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain(name=name, delegated=delegated)
        d.clean()
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        self.arpa = self.create_domain(name='arpa')
        self.arpa.save()
        self.i_arpa = self.create_domain(name='in-addr.arpa')
        self.i_arpa.save()

        self.c = Domain(name="ccc")
        self.c.save()
        self.f_c = Domain(name="foo.ccc")
        self.f_c.save()
        self.r1 = self.create_domain(name="10")
        self.r1.save()
        self.n = System(hostname="foo.mozilla.com")
        self.n.clean()
        self.n.save()

    def do_add_sreg(self, label, domain, ip_str, ip_type='4'):
        r = StaticReg(
            label=label, domain=domain, ip_str=ip_str, ip_type=ip_type,
            system=self.n
        )
        r.full_clean()
        r.save()
        repr(r)
        return r

    def do_add_ptr(self, label, domain, ip_str, ip_type='4'):
        ptr = PTR.objects.create(
            name=label + '.' + domain.name, ip_str=ip_str, ip_type=ip_type
        )
        return ptr

    def test1_conflict_add_sreg_first(self):
        # PTRdd an sreg and make sure PTR can't exist.
        label = "foo4"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_sreg(**kwargs)
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_ptr, **kwargs)

    def test1_conflict_add_PTR_first(self):
        # Add an PTR and make sure an sreg can't exist.
        label = "foo5"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_ptr(**kwargs)
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.assertRaises(ValidationError, self.do_add_sreg, **kwargs)

    def test2_conflict_add_sreg_first(self):
        # Add an sreg and update an existing PTR to conflict. Test for
        # exception.
        label = "fo99"
        domain = self.f_c
        ip_str = "10.0.0.2"
        kwargs = {'label': label, 'domain': domain,
                  'ip_str': ip_str}
        self.do_add_sreg(**kwargs)
        ip_str = "10.0.0.3"
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        ptr = self.do_add_ptr(**kwargs)
        ptr.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, ptr.clean)

    def test2_conflict_add_A_first(self):
        # Add an PTR and update and existing sreg to conflict. Test for
        # exception.
        label = "foo98"
        domain = self.f_c
        ip_str = "10.0.0.2"
        # Add PTR
        kwargs = {'label': label, 'domain': domain, 'ip_str': ip_str}
        self.do_add_ptr(**kwargs)

        # Add StaticReg with diff IP
        ip_str = "10.0.0.3"
        kwargs = {'label': label, 'domain': domain,
                  'ip_str': ip_str}
        sreg = self.do_add_sreg(**kwargs)

        # Conflict the IP on the sreg
        sreg.ip_str = "10.0.0.2"
        self.assertRaises(ValidationError, sreg.save)
