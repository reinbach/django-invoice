from django.contrib import admin
from invoice.models import Invoice, InvoiceItem, InvoiceSettings


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline, ]
    search_fields = ('uid', 'contractor__name', 'subscriber__name')
    list_display = (
        'uid',
        'state',
        'total_amount',
        'date_issuance',
        'date_paid',
    )


class InvoiceSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    # action to generate example invoice

admin.site.register(InvoiceSettings, InvoiceSettingsAdmin)
admin.site.register(Invoice, InvoiceAdmin)
