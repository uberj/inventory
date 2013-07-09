from django.test import TestCase

from mozdns.soa.models import SOA
import datetime


class SOAIncrementTests(TestCase):

    def to_date(self, date):
        year, month, day = map(lambda s: int(s), (
            date[:4], date[4:6], date[6:]
        ))
        return datetime.date(year, month, day)

    def test_serial_equal_date(self):
        # Case ==
        serial = '2111111111'
        date = self.to_date('21111111')
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(serial) + 1, new_serial)

    def test_serial_less_than_date(self):
        # Case serial < date
        serial = '2111101111'
        date_str = '21111111'
        date = self.to_date(date_str)
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(date_str + '00'), new_serial)

    def test_serial_greater_than_date(self):
        # Case serial > date
        serial = '2111111111'
        date = self.to_date('21111011')
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(serial) + 1, new_serial)

    def test_incremented_serial(self):
        soa = SOA.objects.create(
            description="foobar baz", contact='fooba.mozilla.com',
            primary='ns1.mozilla.com')

        old_serial = soa.serial
        new_serial = soa.get_incremented_serial()
        self.assertEqual(old_serial + 1, new_serial)
