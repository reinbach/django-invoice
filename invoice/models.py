# coding: utf-8
from __future__ import division
import os
import random
import string

from io import FileIO, BytesIO
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.http.response import HttpResponse
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.translation import ugettext as _

from invoice.utils import format_currency, load_class

Address = load_class(getattr(settings, 'INVOICE_ADDRESS_MODEL', 'invoice.modelbases.Address'))
BankAccount = load_class(getattr(settings, 'INVOICE_BANK_ACCOUNT_MODEL', 'invoice.modelbases.BankAccount'))
Export = load_class(getattr(settings, 'INVOICE_EXPORT_CLASS', 'invoice.exports.HtmlExport'))


class InvoiceManager(models.Manager):

    def get_due(self):
        return (self.get_query_set()
                    .filter(date_issuance__lte=date.today())
                    .filter(date_paid__isnull=True)
                )


@python_2_unicode_compatible
class Invoice(models.Model):
    STATE_PROFORMA = 'proforma'
    STATE_INVOICE = 'invoice'
    INVOICE_STATES = (
        (STATE_PROFORMA, _("Proforma")),
        (STATE_INVOICE, _("Invoice")),
    )

    uid = models.CharField(unique=True, max_length=10, blank=True)
    contractor = models.ForeignKey(Address, related_name='+')
    contractor_bank = models.ForeignKey(BankAccount, related_name='+', db_index=False,
                                        null=True, blank=True)

    subscriber = models.ForeignKey(Address, related_name='+')
    subscriber_shipping = models.ForeignKey(Address, related_name='+', db_index=False,
                                            null=True, blank=True)
    logo = models.FilePathField(match=".*(png|jpg|jpeg|svg)", null=True, blank=True)
    state = models.CharField(max_length=15, choices=INVOICE_STATES, default=STATE_PROFORMA)

    date_issuance = models.DateField(default=date.today)
    date_due = models.DateField(default=lambda: date.today() + timedelta(days=14))
    date_paid = models.DateField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))

    objects = InvoiceManager()
    export = Export()

    def __str__(self):
        return smart_text("{0} {1} {2}").format(self.state_text, _("nr."), self.id)

    class Meta:
        ordering = ('-date_issuance', 'id')

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = "".join(random.sample(string.ascii_letters + string.digits, 8))
            while self.__class__.objects.filter(uid=self.uid).exists():
                self.uid = "".join(random.sample(string.ascii_letters + string.digits, 8))
        return super(Invoice, self).save(*args, **kwargs)

    @property
    def state_text(self):
        for state in self.INVOICE_STATES:
            if state[0] == self.state:
                return state[1]

    def set_paid(self):
        self.date_paid = date.today()
        self.state = self.STATE_INVOICE
        self.save()

    def add_item(self, description, price, quantity=1):
        InvoiceItem.objects.create(invoice=self, description=description,
                                   unit_price=price, quantity=quantity)

    def total_amount(self):
        '''Returns total as formated string'''
        return format_currency(self.total())

    def total(self):
        '''Computes total price using all items as decimal number'''
        total = Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total

    def get_filename(self):
        return _('{0}-{1}.{2}').format(self.state_text, self.id,
            self.export.get_content_type().rsplit("/", 2)[1])

    def get_info(self):
        """Returns (multiline) string with info printed below contractor"""
        return None

    def get_footer(self):
        """Returns (multiline) string with info in footer"""
        return None

    def export_file(self, basedir):
        filename = os.path.join(basedir, self.get_filename())
        fileio = FileIO(filename, "w")
        self.export.draw(self, fileio)
        fileio.close()
        return filename

    def export_bytes(self):
        stream = BytesIO()
        self.export.draw(self, stream)
        output = stream.getvalue()
        stream.close()
        return output

    def export_attachment(self):
        attachment = MIMEApplication(self.export_bytes())
        attachment.add_header("Content-Disposition", "attachment", filename=self.get_filename())
        return attachment

    def export_response(self):
        response = HttpResponse(content_type=self.export.get_content_type())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.get_filename())
        response.write(self.export_bytes())
        return response


@python_2_unicode_compatible
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        ordering = ['unit_price']

    def total(self):
        total = Decimal(str(self.unit_price * self.quantity))
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.description
