from __future__ import absolute_import
import datetime
import os

from django.test import TestCase
from invoice.models import Invoice, InvoiceSetting

from invoice import test_data


class InvoiceTest(TestCase):

    def setUp(self):
        self.invoice = test_data.load()

    def testGetDue(self):
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.set_paid()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

    def test_get_due2(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.invoice.date_issuance = yesterday
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.date_issuance = tomorrow
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

    def test_generate_pdf(self):
        basedir = "/tmp"
        if self.invoice.logo:
            self.failUnless(os.path.exists(self.invoice.logo))
        filename = self.invoice.export_file(basedir)
        self.failUnless(os.path.exists(filename))
        stats = os.stat(filename)
        self.failIf(stats.st_size < 100)  # the file has to contain something


class InvoiceSettingTest(TestCase):

    def setUp(self):
        self.invoice = test_data.load()
        self.settings, c = InvoiceSetting.objects.get_or_create(
            name="Test settings",
            defaults=dict(
                line_color="50,50,128",
                info_text=u"Pay in time the invoice {{ invoice.id }}",
                footer_text="According to legal laws blabla... {{ invoice.state }}"
            )
        )

    def test_invoice_settings(self):
        # clear the settings cache in invoice
        if hasattr(self.invoice, "settings"):
            del self.invoice.settings
        self.failIf(hasattr(self.invoice, "settings"))
        if self.invoice.logo:
            self.failUnless(os.path.exists(self.invoice.logo))

        self.failIfEqual(self.invoice.get_settings(), None)
        self.invoice.settings = self.settings
        filename = self.invoice.export_file("/tmp")
        self.failUnless(os.path.exists(filename))
        stats = os.stat(filename)
        self.failIf(stats.st_size < 100)  # the file has to contain something

    def test_setting_color(self):
        self.settings.line_color = "1,1,1,1"
        self.settings.save()
        self.failIf(self.settings.color)  # color has to return empty list
        self.failUnlessEqual(self.settings.color or (1, 1, 1), (1, 1, 1))

        self.settings.line_color = "128,128,128"
        self.settings.save()
        self.failUnlessEqual(self.settings.color, [0.5, 0.5, 0.5])
