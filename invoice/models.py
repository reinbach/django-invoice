
from datetime import date
from decimal import Decimal
from StringIO import StringIO
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage

from invoice.utils import format_currency, friendly_id, load_class
from invoice.pdf import draw_pdf


Address = load_class(getattr(settings, 'INVOICE_ADDRESS_MODEL', 'invoice.modelbases.Address'))

USER_CLASS = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class InvoiceManager(models.Manager):
    def get_invoiced(self):
        return self.filter(invoiced=True, draft=False)

    def get_due(self):
        return self.filter(invoice_date__lte=date.today(),
                           invoiced=False,
                           draft=False)


class Invoice(models.Model):
    user = models.ForeignKey(USER_CLASS, null=True)
    address = models.ForeignKey(Address, related_name='%(class)s_set')
    invoice_id = models.CharField(unique=True, max_length=6,
                                  null=True, blank=True, editable=False)
    invoice_date = models.DateField(default=date.today)
    invoiced = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))

    objects = InvoiceManager()

    def __unicode__(self):
        return u'%s (%s)' % (self.invoice_id, self.total_amount())

    class Meta:
        ordering = ('-invoice_date', 'id')

    def save(self, *args, **kwargs):
        super(Invoice, self).save(*args, **kwargs)

        if not self.invoice_id:
            self.invoice_id = friendly_id.encode(self.pk)
            kwargs['force_insert'] = False
            super(Invoice, self).save(*args, **kwargs)

    def total_amount(self):
        return format_currency(self.total())

    def total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total

    def file_name(self):
        return u'Invoice %s.pdf' % self.invoice_id

    def send_invoice(self, subject="Invoice", text=""):
        pdf = StringIO()
        draw_pdf(pdf, self)
        pdf.seek(0)

        attachment = MIMEApplication(pdf.read())
        attachment.add_header("Content-Disposition", "attachment", filename=self.file_name())
        pdf.close()

        email = EmailMessage(subject=subject, body=text, to=[self.user.email])
        email.attach(attachment)
        email.send()

        self.invoiced = True
        self.save()


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
