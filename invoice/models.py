# coding: utf-8
from __future__ import division
import os
from io import FileIO, BytesIO
from datetime import date, timedelta
from decimal import Decimal
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.http.response import HttpResponse
from django.template import Template, Context
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.translation import ugettext as _

from invoice.utils import format_currency, load_class, model_to_dict
from invoice.export import PdfExport

Address = load_class(getattr(settings, 'INVOICE_ADDRESS_MODEL', 'invoice.modelbases.Address'))
BankAccount = load_class(getattr(settings, 'INVOICE_BANK_ACCOUNT_MODEL', 'invoice.modelbases.BankAccount'))


@python_2_unicode_compatible
class InvoiceSetting(models.Model):
    '''The class modifies texts and appearance of generated invoice.
    Automatically the first style will be used for every invoice if
    you don't assign another settings into `instance.settings`.
    If you don't want to use these settings just don't create any.
    '''
    STYLE_CHOICES = (
        ('bold', _("Bold")),
        ('italic', _("Italic")),
    )
    name = models.CharField(max_length=20, help_text=_('For your internal identification'))
    info_text = models.TextField(help_text=_("The text will be rendered as a template above ITEMS part. "
                                             "You have `invoice` variable available here"))
    footer_text = models.TextField(help_text=_("The text will be rendered as a template on the bottom of an invoice. "
                                               "You have `invoice` variable available here"))
    line_color = models.CommaSeparatedIntegerField(default="200,128,128", max_length=11,
                                                   help_text=_('Three comma separated values <0, 255> (R,G,B values)'))

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return self.name

    def info(self, context):
        return Template(self.info_text).render(Context(context))

    def footer(self, context):
        return Template(self.footer_text).render(Context(context))

    @property
    def color(self):
        colors = []
        if not self.line_color:
            return colors
        try:
            colors_str = self.line_color.split(",")
            if len(colors_str) != 3:
                return colors
            for value in colors_str:
                color = int(value)/256
                if color < 0 or color > 1: raise ValueError("Color is not in interval 0, 256")
                colors.append(color)
        except ValueError:
            return ()
        return colors


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

    # uid = models.CharField(unique=True, max_length=10, blank=True)
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
        return smart_text("{0} {1} {2}").format(self.state_text, _("nr."), self.id)

    class Meta:
        ordering = ('-date_issuance', 'id')

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
        return format_currency(self.total())

    def total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total

    def get_filename(self):
        return _('{0}-{1}.pdf').format(self.state_text, self.id)

    def get_settings(self):
        # how to make it right?
        if not hasattr(self, "settings"):
            if InvoiceSetting.objects.count() >= 1:
                setattr(self, "settings", InvoiceSetting.objects.all()[0])
            else:
                setattr(self, "settings", None)
        return self.settings

    def export_file(self, basedir):
        filename = os.path.join(basedir, self.get_filename())
        fileio = FileIO(filename, "w")
        self.export.draw(self, fileio)
        fileio.close()
        return filename

    def export_bytes(self, settings=None):
        stream = BytesIO()
        self.export.draw(self, stream)
        output = stream.getvalue()
        stream.close()
        return output

    def export_attachment(self, settings=None):
        attachment = MIMEApplication(self.export_bytes())
        attachment.add_header("Content-Disposition", "attachment", filename=self.get_filename())
        return attachment

    def export_response(self, settings=None):
        response = HttpResponse(content_type=self.export.get_content_type())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.get_filename())
        response.write(self.export_bytes())
        return response


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    class Meta:
        ordering = ['unit_price']

    def total(self):
        total = Decimal(str(self.unit_price * self.quantity))
        return total.quantize(Decimal('0.01'))

    def __unicode__(self):
        return self.description
