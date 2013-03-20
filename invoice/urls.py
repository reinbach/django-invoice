# coding: utf-8
from django.conf.urls import patterns, url
from django.utils.translation import gettext

from invoice.views import download_pdf


urlpatterns = patterns(
    '',
    url('^{0}/(?P<uid>[a-zA-Z0-9]+)$'.format(gettext("invoice")),  download_pdf, name="invoice"),
)
