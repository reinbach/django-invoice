# coding: utf-8
import os
from io import FileIO, BytesIO
from datetime import date, timedelta
from decimal import Decimal
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.http.response import HttpResponse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from invoice.utils import format_currency, friendly_id, load_class, model_to_dict
from invoice.export import PdfExport

Address = load_class(getattr(settings, 'INVOICE_ADDRESS_MODEL', 'invoice.modelbases.Address'))
BankAccount = load_class(getattr(settings, 'INVOICE_BANK_ACCOUNT_MODEL', 'invoice.modelbases.BankAccount'))


@python_2_unicode_compatible
class InvoiceSettings(models.Model):
    SECTIONS = (
        ('header', _("Header")),
        ('contractor', _("Contractor")),
        ('subscriber', _("Subscriber")),
        ('itemlist', _("Item list")),
        ('footer', _("Footer")),
    )
    STYLE_CHOICES = (
        ('bold', _("Bold")),
        ('italic', _("Italic")),
    )

    section = models.CharField(max_length=20, choices=SECTIONS)
    template = models.TextField()
    foreground = models.CharField(max_length=6, null=True, blank=True)
    background = models.CharField(max_length=6, null=True, blank=True)
    font_size = models.PositiveSmallIntegerField(default=12)
    font_style = models.CharField(max_length=10, choices=STYLE_CHOICES)

    def __str__(self):
        return self.section


class InvoiceManager(models.Manager):

    def get_due(self):
        return (self.get_query_set()
                    .filter(date_issuance__lte=date.today())
                    .filter(state=Invoice.STATE_PROFORMA)
                )


@python_2_unicode_compatible
class Invoice(models.Model):
    STATE_PROFORMA = 'proforma'
    STATE_INVOICE = 'invoice'
    INVOICE_STATES = (
        (STATE_PROFORMA, _("Proforma")),
        (STATE_INVOICE, _("Invoice")),
    )

    uid = models.CharField(unique=True, max_length=6, blank=True, editable=False)
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
    export = PdfExport()

    def __str__(self):
        return u'%s (%s)' % (self.uid, self.total_amount())

    class Meta:
        ordering = ('-date_issuance', 'uid')

    def save(self, *args, **kwargs):
        super(Invoice, self).save(*args, **kwargs)
        if not self.uid:
            self.uid = friendly_id.encode(self.pk)
            kwargs['force_insert'] = False
            super(Invoice, self).save(*args, **kwargs)

    def set_paid(self):
        self.date_paid = date.today()
        self.state = self.STATE_INVOICE
        self.save()

    def total_amount(self):
        return format_currency(self.total())

    def total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total

    def get_filename(self):
        return _('Invoice-{uid}.pdf').format(**model_to_dict(self))

    def export_file(self, basedir):
        filename = os.path.join(basedir, self.get_filename())
        fileio = FileIO(filename, "w")
        self.export.draw(self, fileio)
        fileio.close()

    def export_bytes(self):
        stream = BytesIO()
        self.export.draw(self, stream)
        output = stream.get_value()
        stream.close()
        return output

    def export_attachment(self):
        attachment = MIMEApplication(self.export_bytes())
        attachment.add_header("Content-Disposition", "attachment", filename=self.get_filename())
        return attachment

    def export_response(self):
        response = HttpResponse(content_type=self.export.get_content_type())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.get_filename())
        response.write(self.export_bytes)
        return response


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    def total(self):
        total = Decimal(str(self.unit_price * self.quantity))
        return total.quantize(Decimal('0.01'))

    def __unicode__(self):
        return self.description
