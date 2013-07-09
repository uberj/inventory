from django.test import TestCase

from mozdns.soa.models import SOA


class SOAIncrementTests(TestCase):
    def test_serial_equal_date(self):
        # Case ==
        serial = '1111223344'
        date = '11112233'
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(serial) + 1, new_serial)

    def test_serial_less_than_date(self):
        # Case serial < date
        serial = '1111223244'
        date = '11112233'
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(date + '00'), new_serial)

    def test_serial_greater_than_date(self):
        # Case serial > date
        serial = '1111223444'
        date = '11112233'
        new_serial = SOA.calc_serial(serial, date)
        self.assertEqual(int(serial) + 1, new_serial)

    def test_malformed_serial(self):
        # bad serial
        serial = '11111223444'
        date = '11112233'
        self.assertRaises(AssertionError, SOA.calc_serial, *(serial, date))

    def test_malformed_date(self):
        # bad date
        serial = '1111223444'
        date = '113112233'
        self.assertRaises(AssertionError, SOA.calc_serial, *(serial, date))

    def test_incremented_serial(self):
        soa = SOA.objects.create(
            description="foobar baz", contact='fooba.mozilla.com',
            primary='ns1.mozilla.com')

        old_serial = soa.serial
        new_serial = soa.get_incremented_serial()
        self.assertEqual(old_serial + 1, new_serial)
