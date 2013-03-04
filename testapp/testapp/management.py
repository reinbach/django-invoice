from django.db.models.signals import post_syncdb

import invoice.models


def test_data(sender, **kwargs):
    a1, c = invoice.models.Address.objects.get_or_create(name="John Test", defaults={
        "street": "Testing 1",
        "town": "SQLite 3",
        "postcode": "NA162 33",
        "business_id": "1094658934",
        "tax_id": "GB6349013764",
        "extra": "Phone: 0384-7364-366\nEmail: tst@mailinator.com"
    })

    a2, c = invoice.models.Address.objects.get_or_create(name="George Passing", defaults={
        "street": "Passing 9",
        "town": "PostgreSQL 9.3",
        "postcode": "638 00",
    })

    b, c = invoice.models.BankAccount.objects.get_or_create(number="1234567", defaults={
        "prefix": "64922",
        "bank": "2045"
    })

    i, c = invoice.models.Invoice.objects.get_or_create(uid="10001", contractor=a1, subscriber=a2,
                                                        contractor_bank=b)

post_syncdb.connect(test_data, sender=invoice.models)
