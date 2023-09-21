# This file is part of cloud-init. See LICENSE file for license information.

import re

from cloudinit.distros.parsers import resolv_conf
from tests.unittests.helpers import TestCase

BASE_RESOLVE = """
; generated by /sbin/dhclient-script
search blah.yahoo.com yahoo.com
nameserver 10.15.44.14
nameserver 10.15.30.92
"""
BASE_RESOLVE = BASE_RESOLVE.strip()


class TestResolvHelper(TestCase):
    def test_parse_same(self):
        rp = resolv_conf.ResolvConf(BASE_RESOLVE)
        rp_r = str(rp).strip()
        self.assertEqual(BASE_RESOLVE, rp_r)

    def test_local_domain(self):
        rp = resolv_conf.ResolvConf(BASE_RESOLVE)
        self.assertIsNone(rp.local_domain)

        rp.local_domain = "bob"
        self.assertEqual("bob", rp.local_domain)
        self.assertIn("domain bob", str(rp))

    def test_nameservers(self):
        rp = resolv_conf.ResolvConf(BASE_RESOLVE)

        # Start with two nameservers that already appear in the configuration.
        self.assertIn("10.15.44.14", rp.nameservers)
        self.assertIn("10.15.30.92", rp.nameservers)

        # Add a third nameserver and verify it appears in the resolv.conf.
        rp.add_nameserver("10.2")
        self.assertIn("10.2", rp.nameservers)
        self.assertIn("nameserver 10.2", str(rp))
        self.assertEqual(len(rp.nameservers), 3)

        # Add a fourth nameserver and verify it appears in the resolv.conf.
        rp.add_nameserver("10.3")
        self.assertIn("10.3", rp.nameservers)
        self.assertIn("nameserver 10.3", str(rp))
        self.assertEqual(len(rp.nameservers), 4)

    def test_search_domains(self):
        rp = resolv_conf.ResolvConf(BASE_RESOLVE)
        self.assertIn("yahoo.com", rp.search_domains)
        self.assertIn("blah.yahoo.com", rp.search_domains)
        rp.add_search_domain("bbb.y.com")
        self.assertIn("bbb.y.com", rp.search_domains)
        self.assertTrue(re.search(r"search(.*)bbb.y.com(.*)", str(rp)))
        self.assertIn("bbb.y.com", rp.search_domains)
        rp.add_search_domain("bbb.y.com")
        self.assertEqual(len(rp.search_domains), 3)
        rp.add_search_domain("bbb2.y.com")
        self.assertEqual(len(rp.search_domains), 4)
        rp.add_search_domain("bbb3.y.com")
        self.assertEqual(len(rp.search_domains), 5)
        rp.add_search_domain("bbb4.y.com")
        self.assertEqual(len(rp.search_domains), 6)
        self.assertRaises(ValueError, rp.add_search_domain, "bbb5.y.com")
        self.assertEqual(len(rp.search_domains), 6)
