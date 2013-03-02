from django.db import models
from django.utils.translation import ugettext as _
from django.utils.encoding import python_2_unicode_compatible
from invoice.utils import model_to_dict


@python_2_unicode_compatible
class Address(models.Model):

    name = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    town = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=20)

    business_id = models.CharField(_("Business ID"), max_length=12, null=True, blank=True)
    tax_id = models.CharField(_("Tax ID"), max_length=15, null=True, blank=True)

    extra = models.TextField(null=True, blank=True)

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
    '''Bank account. Mandatory for SHOP'''
    prefix = models.DecimalField(_('Prefix'), null=True, blank=True,
                                 max_digits=15, decimal_places=0)
    number = models.DecimalField(_('Account number'), decimal_places=0,
                                 max_digits=16)
    bank = models.DecimalField(_('Bank code'), decimal_places=0, max_digits=4)

    def __str__(self):
        if not self.prefix:
            return u"{0} / {1}".format(self.number, self.bank)
        return u"{0} - {1} / {2}".format(self.prefix, self.number, self.bank)
