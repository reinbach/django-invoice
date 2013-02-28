from django.core import exceptions
from django.http import HttpResponse
from django.utils.importlib import import_module


def format_currency(amount):
    return unicode(amount)
    # return u"%s %.2f %s" % (
    #     settings.INV_CURRENCY_SYMBOL, amount, settings.INV_CURRENCY
    # )


def pdf_response(draw_funk, file_name, *args, **kwargs):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=\"%s\"" % file_name
    draw_funk(response, *args, **kwargs)
    return response


def send_invoices():
    from ..models import Invoice

    for invoice in Invoice.objects.get_due():
        invoice.send_email()


def load_class(class_path, setting_name=None):
    """
    Loads a class given a class_path. The setting value may be a string or a
    tuple.

    The setting_name parameter is only there for pretty error output, and
    therefore is optional
    """
    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        if setting_name:
            txt = '%s isn\'t a valid module. Check your %s setting' % (
                class_path, setting_name)
        else:
            txt = '%s isn\'t a valid module.' % class_path
        raise exceptions.ImproperlyConfigured(txt)

    try:
        mod = import_module(class_module)
    except ImportError, e:
        if setting_name:
            txt = 'Error importing backend %s: "%s". Check your %s setting' % (
                class_module, e, setting_name)
        else:
            txt = 'Error importing backend %s: "%s".' % (class_module, e)
        raise exceptions.ImproperlyConfigured(txt)

    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        if setting_name:
            txt = ('Backend module "%s" does not define a "%s" class. Check'
                   ' your %s setting' % (class_module, class_name, setting_name))
        else:
            txt = 'Backend module "%s" does not define a "%s" class.' % (
                class_module, class_name)
        raise exceptions.ImproperlyConfigured(txt)
    return clazz
