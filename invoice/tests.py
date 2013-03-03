import datetime
import os

from django.test import TestCase
from invoice.models import Invoice

from invoice import test_data


class InvoiceTest(TestCase):

    def setUp(self):
        self.invoice = test_data.load()

    def testGetDue(self):
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.set_paid()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.invoice.state = Invoice.STATE_PROFORMA
        self.invoice.date_issuance = yesterday
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.date_issuance = tomorrow
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

    def test_generate_pdf(self):
        basedir = "/tmp"
        self.failUnless(self.invoice.logo)
        self.invoice.export_file(basedir)
        self.failUnless(os.path.exists(os.path.join(basedir, self.invoice.get_filename())))
