# coding: utf-8
import os
import pytest

from decimal import Decimal
from invoice.models import Invoice, InvoiceItem, Address, BankAccount


@pytest.fixture
def invoice():
    contractor, created = Address.objects.get_or_create(
        name='Simon Luijk',
        street=u'Rydsvägen 242',
        town=u'Linköping',
        defaults=dict(
            postcode='584 64',
            country=u"Sweden",
            business_id="523489473",
            tax_id="US092748793",
            extra=(
                'Phone: 076-577-9284\n'
                'Email: boss@example.com'
            )
        )
    )

    subscriber, created = (Address.objects.get_or_create(
        name=u'Tomáš Peterka',
        street=u'Zdislavická',
        town=u'Praha',
        defaults=dict(
            postcode='142 00',
            country=u"Czech Republic",
            extra="Email: atheiste@seznam.cz"
        )
    ))

    account, created = BankAccount.objects.get_or_create(
        number=782634210, bank=6250)

    basedir = os.path.dirname(os.path.abspath(__file__))
    logo = os.path.join(basedir, "logo.png")
    if not os.path.exists(logo):
        logo = None

    inv, c = Invoice.objects.get_or_create(
        contractor=contractor,
        subscriber=subscriber,
        defaults=dict(logo=logo, contractor_bank=account)
    )

    InvoiceItem.objects.get_or_create(
        invoice=inv, description="Bunch of cow-horse meat",
        defaults={"quantity": 10, "unit_price": Decimal("550.00")})
    InvoiceItem.objects.get_or_create(
        invoice=inv, description="World peace",
        defaults={"quantity": 1, "unit_price": Decimal("999999.99")})
    InvoiceItem.objects.get_or_create(
        invoice=inv, description="IKEA flashlight",
        defaults={"quantity": 1, "unit_price": Decimal("4.50")})
    InvoiceItem.objects.get_or_create(
        invoice=inv, description="Sweet dream",
        defaults={"quantity": 2, "unit_price": Decimal("0.00")})

    return inv
