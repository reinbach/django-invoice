from django.shortcuts import get_object_or_404
from invoice.models import Invoice


def download(request, uid):
    invoice = get_object_or_404(Invoice, uid=uid)
    return invoice.export_response()
