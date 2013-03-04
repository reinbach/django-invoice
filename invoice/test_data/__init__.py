# coding: utf-8
import os
from invoice.models import Invoice, Address, BankAccount


def load():
    contractor, created = (Address.objects
                                  .get_or_create(name='Simon Luijk',
                                                 street=u'Rydsvägen 242',
                                                 town=u'Linköping',
                                                 defaults=dict(
                                                     postcode='584 64',
                                                     country=u"Sweden",
                                                     business_id="523489473",
                                                     tax_id="US092748793",
                                                     extra=('Phone: 076-577-9284\n'
                                                            'Email: boss@example.com')
                                                 )))

    subscriber, created = (Address.objects
                                  .get_or_create(name=u'Tomáš Peterka',
                                                 street=u'Zdislavická',
                                                 town=u'Praha',
                                                 defaults=dict(
                                                     postcode='142 00',
                                                     country=u"Czech Republic",
                                                     extra="Email: atheiste@seznam.cz"
                                                 )
                                                 )
                           )
    account, created = BankAccount.objects.get_or_create(number=782634210, bank=6250)

    basedir = os.path.dirname(os.path.abspath(__file__))
    logo = os.path.join(basedir, "logo.png")
    if not os.path.exists(logo):
        logo = None

    invoice, c = Invoice.objects.get_or_create(uid="30003", defaults=dict(contractor=contractor,
                                               subscriber=subscriber, logo=logo,
                                               contractor_bank=account))
    return invoice
