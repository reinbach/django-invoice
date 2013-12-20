from __future__ import absolute_import
import datetime
import os

from django.test import TestCase
from invoice.models import Invoice

from invoice import test_data


class InvoiceTest(TestCase):

    def setUp(self):
        self.invoice = test_data.load()

    def testGetDue(self):
        self.assertEqual(Invoice.objects.get_due().count(), 1)

        self.invoice.set_paid()
        self.assertEqual(Invoice.objects.get_due().count(), 0)

    def test_get_due2(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.invoice.date_issuance = yesterday
        self.invoice.save()
        self.assertEqual(Invoice.objects.get_due().count(), 1)

        self.invoice.date_issuance = tomorrow
        self.invoice.save()
        self.assertEqual(Invoice.objects.get_due().count(), 0)

    def test_generate_file(self):
        basedir = "/tmp"
        if self.invoice.logo:
            self.assertTrue(os.path.exists(self.invoice.logo))
        filename = self.invoice.export_file(basedir)
        self.assertTrue(os.path.exists(filename))
        stats = os.stat(filename)
        self.assertTrue(stats.st_size > 10)  # the file has to contain something
        os.unlink(filename)
