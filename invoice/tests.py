import datetime
import os

from django.test import TestCase
from invoice.models import Invoice, InvoiceSettings

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
        filename = self.invoice.export_file(basedir)
        self.failUnless(os.path.exists(filename))

    def test_invoice_settings(self):
        # generate new filename
        self.invoice.uid = "SETTINGS01"
        # clear the settings cache in invoice
        if hasattr(self.invoice, "settings"):
            del self.invoice.settings
        self.failIf(hasattr(self.invoice, "settings"))

        InvoiceSettings.objects.create(name="Test settings",
            info_text=u"Pay in time the invoice {{ invoice.uid }}",
            footer_text="According to legal laws blabla... {{ invoice.state }}")
        self.failUnlessEqual(InvoiceSettings.objects.count(), 1)

        self.failIfEqual(self.invoice.get_settings(), None)
        filename = self.invoice.export_file("/tmp")
        self.failUnless(os.path.exists(filename))
