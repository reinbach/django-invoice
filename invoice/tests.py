import datetime
from io import FileIO

from django.test import TestCase

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except:
    from django.contrib.auth.models import User

from invoice.models import Invoice, Address
from invoice.pdf import draw_pdf


class InvoiceTestCase(TestCase):
    def setUp(self):
        usr = User.objects.create(username='test',
                                  first_name='John',
                                  last_name='Doe',
                                  email='example@example.com')

        address = Address.objects.create(contact_name='John Doe',
                                         address_one='Street',
                                         town='Town',
                                         postcode='PostCode',
                                         country="Country")

        self.inv = Invoice.objects.create(user=usr, address=address)

    def testInvoiceId(self):
        inv = self.inv
        self.assertEquals(inv.invoice_id, u'TTH9R')

        inv.invoice_id = False
        inv.save()

        self.assertEquals(inv.invoice_id, u'TTH9R')

    def testGetDue(self):
        inv = self.inv

        inv.draft = True
        inv.save()
        self.assertEquals(len(Invoice.objects.get_due()), 0)

        inv.draft = False
        inv.save()
        self.assertEquals(len(Invoice.objects.get_due()), 1)

        inv.invoiced = True
        inv.save()
        self.assertEquals(len(Invoice.objects.get_due()), 0)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(1)
        tomorrow = today + datetime.timedelta(1)

        inv.invoiced = False
        inv.invoice_date = yesterday
        inv.save()
        self.assertEquals(len(Invoice.objects.get_due()), 1)

        inv.invoice_date = tomorrow
        inv.save()
        self.assertEquals(len(Invoice.objects.get_due()), 0)

    def test_generate_pdf(self):
        filename = "/tmp/invoice.pdf"
        fileio = FileIO(filename, "w")
        draw_pdf(fileio, self.inv)
        fileio.close()
