from django.shortcuts import get_object_or_404
from invoice.models import Invoice


def pdf_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return invoice.export_response()
