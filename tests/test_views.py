import unittest
from views import *
import asyncio
import json


class TestResolveAddress(unittest.TestCase):
    def test_resolve_address(self):
        # Test a valid address
        search_term = "38 Upper Montagu Street, Marylebone W1H 1LJ, United Kingdom"
        address = resolve_address(search_term)
        self.assertEqual(address.street, "Upper Montagu Street")
        self.assertEqual(address.line1, "38")
        self.assertEqual(address.line2, "Marylebone")
        self.assertEqual(address.postcode, "W1H 1LJ")
        self.assertEqual(address.country, "United Kingdom")

        # Test an invalid address
        search_term = "Invalid address"
        self.assertRaises(Exception, resolve_address, search_term)

    def test_invalid_address(self):
        # Test an invalid address
        search_term = 'Invalid address'
        with self.assertRaises(Exception):
            resolve_address(search_term)


if __name__ == '__main__':
    unittest.main()
