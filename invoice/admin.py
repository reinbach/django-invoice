from django.contrib import admin
from django.conf.urls.defaults import patterns
from invoice.models import Invoice, InvoiceItem
from invoice.views import pdf_view
from invoice.forms import InvoiceAdminForm


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline, ]
    search_fields = ('invoice_id', )
    list_display = (
        'uid',
        'state',
        'total_amount',
        'invoice_date',
        'paid_date',
    )
    form = InvoiceAdminForm

    def get_urls(self):
        urls = super(InvoiceAdmin, self).get_urls()
        return patterns('',
            (r'^(.+)/pdf/$', self.admin_site.admin_view(pdf_view))
        ) + urls

    send_invoice.short_description = "Send invoice to client"


admin.site.register(Invoice, InvoiceAdmin)
