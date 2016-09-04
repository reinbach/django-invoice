# coding: utf-8
from __future__ import division
import os
import random
import string

from io import FileIO, BytesIO
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import (
    ugettext_lazy as lazy_,
    ugettext as _
)

from invoice.utils import format_currency, load_class

DEFAULT_ADDRESS_MODEL = 'invoice.Address'
DEFAULT_BANKACCOUNT_MODEL = 'invoice.BankAccount'

AddressModel = getattr(settings, 'INVOICE_ADDRESS_MODEL', DEFAULT_ADDRESS_MODEL)
BankAccountModel = getattr(settings, 'INVOICE_BANK_ACCOUNT_MODEL', DEFAULT_BANKACCOUNT_MODEL)
ExportClass = load_class(getattr(settings, 'INVOICE_EXPORT_CLASS', 'invoice.exports.HtmlExport'))


@python_2_unicode_compatible
class Address(models.Model):
    """Address to be printed to Invoice - the method `as_text` is mandatory."""

    name = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    town = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=20)

    business_id = models.CharField(_("Business ID"), max_length=12, null=True, blank=True)
    tax_id = models.CharField(_("Tax ID"), max_length=15, null=True, blank=True)

    extra = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "invoice"
        verbose_name_plural = lazy_("Addresses")

    def __str__(self):
        return u"{0}, {1}".format(self.name, self.street)

    def as_text(self):
        self_dict = model_to_dict(self)
        base = (u"{name}\n"
                u"{street}\n"
                u"{postcode} {town}".format(**self_dict))

        if self.business_id:
            business_info = u"{0}: {1}".format(_("Reg No"), self.business_id)
            tax_info = u"{0}: {1}".format(_("Tax No"), self.tax_id)
            base = u"\n".join((base, business_info, tax_info))

        if self.extra:
            base = u"\n\n".join((base, self.extra))

        return base


@python_2_unicode_compatible
class BankAccount(models.Model):
    """Bank account. Mandatory for SHOP"""
    prefix = models.DecimalField(_('Prefix'), null=True, blank=True,
                                 max_digits=15, decimal_places=0)
    number = models.DecimalField(_('Account number'), decimal_places=0,
                                 max_digits=16)
    bank = models.DecimalField(_('Bank code'), decimal_places=0, max_digits=4)

    class Meta:
        app_label = lazy_("invoice")
        verbose_name = lazy_("bank account")

    def __str__(self):
        if not self.prefix:
            return u"{0} / {1}".format(self.number, self.bank)
        return u"{0} - {1} / {2}".format(self.prefix, self.number, self.bank)

    def as_text(self):
        return u"{0}: {1}".format(_("Bank account"), smart_text(self))



class InvoiceManager(models.Manager):

    def get_due(self):
        return (self.get_queryset()
                    .filter(date_issuance__lte=now().date())
                    .filter(date_paid__isnull=True)
                )


def in_14_days():
    return now().date() + timedelta(days=14)


@python_2_unicode_compatible
class Invoice(models.Model):
    STATE_PROFORMA = 'proforma'
    STATE_INVOICE = 'invoice'
    INVOICE_STATES = (
        (STATE_PROFORMA, _("Proforma")),
        (STATE_INVOICE, _("Invoice")),
    )

    uid = models.CharField(unique=True, max_length=10, blank=True)
    contractor = models.ForeignKey(AddressModel, related_name='+')
    contractor_bank = models.ForeignKey(BankAccountModel, related_name='+', db_index=False,
                                        null=True, blank=True)

    subscriber = models.ForeignKey(AddressModel, related_name='+')
    subscriber_shipping = models.ForeignKey(AddressModel, related_name='+', db_index=False,
                                            null=True, blank=True)
    logo = models.FilePathField(match=".*(png|jpg|jpeg|svg)", null=True, blank=True)
    state = models.CharField(max_length=15, choices=INVOICE_STATES, default=STATE_PROFORMA)

    date_issuance = models.DateField(auto_now_add=True)
    date_due = models.DateField(default=in_14_days)
    date_paid = models.DateField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))

    objects = InvoiceManager()
    export = ExportClass()

    def __str__(self):
        return smart_text("{0} {1} {2}").format(self.state_text, _("nr."), self.id)

    class Meta:
        app_label = "invoice"
        verbose_name = lazy_('invoice')
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
        self.date_paid = now().date()
        self.state = self.STATE_INVOICE
        self.save()

    def add_item(self, description, price, quantity=1):
        if description is not None and price is not None:
            InvoiceItem.objects.create(invoice=self, description=description,
                                       unit_price=price, quantity=quantity)

    def total_amount(self):
        """Return total as formated string."""
        return format_currency(self.total)

    @cached_property
    def total(self):
        """Compute total price using all items as decimal number."""
        x = Decimal('0.00')
        for item in self.items.all():
            x = x + item.total
        return x

    @property
    def filename(self):
        """Deduce unique filename for export."""
        return "{0}-{1}.{2}".format(
            self.state_text,
            self.id,
            self.export.get_content_type().rsplit("/", 2)[1])

    def get_info(self):
        """Return (multiline) string with info printed below contractor."""
        return None

    def get_footer(self):
        """Return (multiline) string with info in footer."""
        return None

    def export_file(self, basedir):
        filename = os.path.join(basedir, self.filename)
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
        attachment.add_header("Content-Disposition", "attachment", filename=self.filename)
        return attachment

    def export_response(self):
        response = HttpResponse(content_type=self.export.get_content_type())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.filename)
        response.write(self.export_bytes())
        return response


@python_2_unicode_compatible
class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        app_label = "invoice"
        verbose_name = lazy_("invoice item")
        ordering = ['unit_price']

    @property
    def total(self):
        total = Decimal(str(self.unit_price * self.quantity))
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.description
