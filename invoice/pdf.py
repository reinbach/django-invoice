from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from django.utils.translation import ugettext as _

from invoice.utils import format_currency


class BasicPdfExporter(object):

    def draw(self, invoice, stream):
        """ Draws the invoice """
        canvas = Canvas(stream, pagesize=A4)
        canvas.translate(0, 29.7*cm)
        canvas.setFont('Helvetica', 10)

        canvas.saveState()
        self.draw_header(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_footer(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_address(invoice, canvas)
        canvas.restoreState()

        # Client address
        textobject = canvas.beginText(1.5*cm, -2.5*cm)
        for line in invoice.subscriber.as_text().split("\n"):
            textobject.textLine(line)
        canvas.drawText(textobject)

        # Info
        textobject = canvas.beginText(1.5*cm, -6.75*cm)
        textobject.textLine(u"{0}: {1}".format(_('Invoice ID'), invoice.uid))
        textobject.textLine(u"{0}: {1}".format(_('Invoice Date'), invoice.invoice_date.strftime('%d %b %Y')))
        textobject.textLine(u"{0}: {1}".format(_('Client'), invoice.subscriber.name))
        canvas.drawText(textobject)

        # Items
        data = [[_('Quantity'), _('Description'), _('Amount'), _('Total')], ]
        for item in invoice.items.all():
            data.append([
                item.quantity,
                item.description,
                format_currency(item.unit_price),
                format_currency(item.total())
            ])
        data.append([u'', u'', _('Total') + u":", format_currency(invoice.total())])
        table = Table(data, colWidths=[2*cm, 11*cm, 3*cm, 3*cm])
        table.setStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,-1), (0.2, 0.2, 0.2)),
            ('GRID', (0,0), (-1,-2), 1, (0.7, 0.7, 0.7)),
            ('GRID', (-2,-1), (-1,-1), 1, (0.7, 0.7, 0.7)),
            ('ALIGN', (-2,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,0), (0.8, 0.8, 0.8)),
        ])
        tw, th, = table.wrapOn(canvas, 15*cm, 19*cm)
        table.drawOn(canvas, 1*cm, -8*cm-th)

        canvas.showPage()
        canvas.save()
        canvas = None

    def draw_header(self, invoice, canvas):
        """ Draws the invoice header """
        canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        canvas.setFont('Helvetica', 16)
        canvas.drawString(2*cm, -1*cm, u"{0} {1}".format(_("Invoice"), invoice.uid))
        # canvas.drawInlineImage(settings.INV_LOGO, 1*cm, -1*cm, 250, 16)
        canvas.setLineWidth(4)
        canvas.line(1.5*cm, -1.3*cm, (21.7 - 1.5)*cm, -1.3*cm)

    def draw_address(self, invoice, canvas):
        """ Draws the business address """
        business_details = (
            u'COMPANY NAME LTD',
            u'STREET',
            u'TOWN',
            U'COUNTY',
            U'POSTCODE',
            U'COUNTRY',
            u'',
            u'',
            u'Phone: +00 (0) 000 000 000',
            u'Email: example@example.com',
            u'Website: www.example.com',
            u'Reg No: 00000000'
        )
        canvas.setFont('Helvetica', 9)
        textobject = canvas.beginText(13*cm, -2.5*cm)
        for line in business_details:
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_footer(self, invoice, canvas):
        """ Draws the invoice footer """
        note = (
            u'Bank Details: Street address, Town, County, POSTCODE',
            u'Sort Code: 00-00-00 Account No: 00000000 (Quote invoice number).',
            u'Please pay via bank transfer or cheque. All payments should be made in CURRENCY.',
            u'Make cheques payable to Company Name Ltd.',
        )
        textobject = canvas.beginText(1*cm, -27*cm)
        for line in note:
            textobject.textLine(line)
        canvas.drawText(textobject)
