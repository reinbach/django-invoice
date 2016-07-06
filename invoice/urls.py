# coding: utf-8
from django.conf.urls import url
from django.utils.translation import gettext
from django.template.defaultfilters import slugify
from invoice.views import download


INVOICE_URL_NAME = slugify(gettext('invoice'))

urlpatterns = [
    url(r'^{0}/(?P<uid>[a-zA-Z0-9]+)/$'.format(INVOICE_URL_NAME), download, name="invoice"),
]
