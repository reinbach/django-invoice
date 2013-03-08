from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext as _
from invoice.models import (Invoice, InvoiceItem, InvoiceSetting,
                            Address, BankAccount)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline, ]
    search_fields = ('id', 'contractor__name', 'subscriber__name')
    list_display = (
        'id',
        'state',
        'total_amount',
        'date_issuance',
        'date_paid',
    )


class InvoiceSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', )
    actions = ['generate_example_invoice', ]

    def generate_example_invoice(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _("Check only one row"))
            return
        if Invoice.objects.count() == 0:
            self.message_user(request, _("The action needs at least one invoice in the database"))
            return
        invoice = Invoice.objects.all()[0]
        invoice.settings = queryset.get()
        return invoice.export_response()
    generate_example_invoice.short_description = _("Generate PDF invoice using checked setting")


admin.site.register(InvoiceSetting, InvoiceSettingAdmin)
admin.site.register(Invoice, InvoiceAdmin)

if not hasattr(settings, "INVOICE_ADDRESS_MODEL"):
    admin.site.register(Address)

if not hasattr(settings, "INVOICE_BANK_ACCOUNT_MODEL"):
    admin.site.register(BankAccount)
