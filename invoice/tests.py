import datetime

from django.test import TestCase

from invoice.models import Invoice, Address
# from invoice.utils import InvoicePdfExport


class InvoiceTestCase(TestCase):
    def setUp(self):
        contractor = Address.objects.create(name='John Doe',
                                            street='Street',
                                            town='Town',
                                            postcode='PostCode',
                                            country="Country",
                                            business_id="523489473",
                                            tax_id="CZ092748793")

        subscriber = Address.objects.create(name='John Doe',
                                            street='Street',
                                            town='Town',
                                            postcode='PostCode',
                                            country="Country")

        self.invoice = Invoice.objects.create(contractor=contractor, subscriber=subscriber)

    def testInvoiceUID(self):
        self.assertEquals(self.invoice.uid, u'TTH9R')

        self.invoice.uid = False
        self.invoice.save()

        self.assertEquals(self.invoice.uid, u'TTH9R')

    def testGetDue(self):
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.set_paid()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.invoice.state = Invoice.STATE_PROFORMA
        self.invoice.invoice_date = yesterday
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 1)

        self.invoice.invoice_date = tomorrow
        self.invoice.save()
        self.assertEquals(Invoice.objects.get_due().count(), 0)

    def test_generate_pdf(self):
        basedir = "/tmp"
        self.invoice.export_file(basedir)
