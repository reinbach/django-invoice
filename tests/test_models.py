from __future__ import absolute_import

import datetime
import os
import pytest

from decimal import Decimal
from django.utils.timezone import now
from invoice.models import Address, BankAccount, Invoice, InvoiceItem


class TestAddress:
    def test_str(self):
        a = Address(name="Home", street="123 Main Street")
        assert str(a) == "Home, 123 Main Street"

    def test_as_text(self):
        a = Address(
            name="Home",
            street="123 Main Street",
            postcode="1234",
            town="Anytown"
        )
        assert a.as_text() == "Home\n123 Main Street\n1234 Anytown"

    def test_as_text_business(self):
        a = Address(
            name="Home",
            street="123 Main Street",
            postcode="1234",
            town="Anytown",
            business_id="4321",
            tax_id="26-0942"
        )
        assert a.as_text() == (
            "Home\n"
            "123 Main Street\n"
            "1234 Anytown\n"
            "Reg No: 4321\n"
            "Tax No: 26-0942"
        )


class TestBankAccount:
    def test_str(self):
        b = BankAccount(number="1234", bank="ACME Bank")
        assert str(b) == "1234 / ACME Bank"

    def test_str_prefix(self):
        b = BankAccount(number="1234", bank="ACME Bank", prefix="Current")
        assert str(b) == "Current - 1234 / ACME Bank"

    def test_as_text(self):
        b = BankAccount(number="1234", bank="ACME Bank")
        assert b.as_text() == "Bank account: 1234 / ACME Bank"


@pytest.mark.django_db
class TestInvoiceManager:
    def test_get_due_paid(self, invoice):
        assert Invoice.objects.get_due().count() == 1

        invoice.set_paid()
        assert Invoice.objects.get_due().count() == 0

    def test_get_due_date(self, invoice):
        today = now().date()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        invoice.date_issuance = yesterday
        invoice.save()
        assert Invoice.objects.get_due().count() == 1

        invoice.date_issuance = tomorrow
        invoice.save()
        assert Invoice.objects.get_due().count() == 0


@pytest.mark.django_db
class TestInvoice:
    def test_set_paid(self, invoice):
        assert invoice.state == Invoice.STATE_PROFORMA
        assert invoice.date_paid is None
        invoice.set_paid()
        assert invoice.state == Invoice.STATE_INVOICE
        assert invoice.date_paid is not None

    def test_generate_file(self, invoice):
        basedir = "/tmp"
        if invoice.logo:
            assert os.path.exists(invoice.logo) is True
        filename = invoice.export_file(basedir)
        assert os.path.exists(filename) is True
        stats = os.stat(filename)
        # the file has to contain something
        assert stats.st_size > 10
        os.unlink(filename)

    def test_add_item(self, invoice):
        item_count = InvoiceItem.objects.all().count()
        assert item_count == 4
        item = invoice.add_item("test", "10.00")
        assert isinstance(item, InvoiceItem)
        InvoiceItem.objects.all().count() == 5
        assert item.description == "test"
        assert item.unit_price == "10.00"
        assert item.quantity == 1

    def test_add_item_price_none(self, invoice):
        item_count = InvoiceItem.objects.all().count()
        assert item_count == 4
        item = invoice.add_item("test", None)
        assert item is None
        InvoiceItem.objects.all().count() == item_count

    def test_add_item_description_none(self, invoice):
        item_count = InvoiceItem.objects.all().count()
        assert item_count == 4
        item = invoice.add_item(None, "10.00")
        assert item is None
        InvoiceItem.objects.all().count() == item_count
