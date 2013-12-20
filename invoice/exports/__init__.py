# coding: utf-8
from django.template.loader import render_to_string


class Export(object):
    """Base exporter class"""

    def get_content_type(self):
        """Returns MIME string of generated format"""
        raise NotImplementedError('Call to abstract method get_content_type')

    def draw(self, invoice, stream):
        """Stream is a binary stream where you should write your data."""
        raise NotImplementedError('Call to abstract method draw')


class HtmlExport(Export):
    def get_content_type(self):
        return u'text/html'

    def draw(self, invoice, stream):
        stream.write(
            render_to_string("invoice/invoice.html", {"invoice": invoice}).encode("utf-8"))
