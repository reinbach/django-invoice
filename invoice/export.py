# coding: utf-8
from os.path import abspath, dirname, join

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from django.utils.translation import ugettext as _

from invoice.utils import format_currency, format_date

STATIC_DIR = join(dirname(abspath(__file__)), "static", "invoice")


class Export(object):
    """Base exporter class"""

    def get_content_type(self):
        """Returns MIME string of generated format"""
        raise NotImplementedError('Call to abstract method get_content_type')

    def draw(self, invoice, stream):
        raise NotImplementedError('Call to abstract method draw')


class PdfExport(Export):
    # A4 size: 21 x 29.7 cm
    FONT_NAME = 'FreeSans'

    def get_content_type(self):
        return u'application/pdf'

    def draw(self, invoice, stream):
        """ Draws the invoice """
        # embed unicode font
        pdfmetrics.registerFont(TTFont('FreeSans', join(STATIC_DIR, 'FreeSans.ttf')))
        addMapping('FreeSans', 0, 0, 'FreeSans')

        self.baseline = -2*cm

        canvas = Canvas(stream, pagesize=A4)
        canvas.translate(0, 29.7*cm)
        canvas.setFont(self.FONT_NAME, 10)

        canvas.saveState()
        self.draw_header(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_subscriber(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_contractor(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_info(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_items(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_footer(invoice, canvas)
        canvas.restoreState()

        canvas.showPage()
        canvas.save()
        canvas = None
        self.baseline = 0

    def draw_header(self, invoice, canvas):
        """ Draws the invoice header """
        canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        canvas.setFont(self.FONT_NAME, 16)
        canvas.drawString(2*cm, self.baseline, u"{0} {1} {2}".format(_("Invoice"), _("Nr."), invoice.uid))
        canvas.drawString((21-6)*cm, self.baseline, format_date(invoice.date_issuance))
        canvas.setLineWidth(3)
        self.baseline -= 0.3*cm
        canvas.line(1.5*cm, self.baseline, (21 - 1.5)*cm, self.baseline)
        self.baseline -= 1*cm

    def draw_subscriber(self, invoice, canvas):
        canvas.setFont(self.FONT_NAME, 13)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        canvas.drawString(1.5*cm, self.baseline, _("The Subscriber"))

        canvas.setFont(self.FONT_NAME, 11)
        canvas.setFillColorRGB(0, 0, 0)
        textobject = canvas.beginText(1.5*cm, self.baseline - .7*cm)
        for line in invoice.subscriber.as_text().split("\n"):
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_contractor(self, invoice, canvas):
        """ Draws the business address """
        canvas.setFont(self.FONT_NAME, 13)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        canvas.drawString(11.5*cm, self.baseline, _("The Contractor"))
        if invoice.logo:
            canvas.drawInlineImage(invoice.logo, (21-1.5-3)*cm, self.baseline - 1.6*cm, 2*cm, 2*cm, True)

        canvas.setFont(self.FONT_NAME, 11)
        canvas.setFillColorRGB(0, 0, 0)
        textobject = canvas.beginText(11.5*cm, self.baseline - .7*cm)
        for line in invoice.contractor.as_text().split("\n"):
            textobject.textLine(line)
        canvas.drawText(textobject)
        self.baseline = -8.3*cm

    def draw_info(self, invoice, canvas):
        # Informations between Contact and Items
        canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
        canvas.setLineWidth(0.5)
        canvas.line(1.5*cm, self.baseline, (21 - 1.5)*cm, self.baseline)

        self.baseline -= .7*cm
        textobject = canvas.beginText(1.5*cm, self.baseline)
        textobject.textLine(u"{0}: {1}".format(_('Date issuance'), format_date(invoice.date_issuance)))
        textobject.textLine(u"{0}: {1}".format(_('Due date'), format_date(invoice.date_due)))
        canvas.drawText(textobject)

        if invoice.contractor_bank:
            textobject = canvas.beginText(11.5*cm, self.baseline)
            for line in invoice.contractor_bank.as_text().split("\n"):
                textobject.textLine(line)
            textobject.textLine(u"{0}: {1}".format(_('Variable symbol'), invoice.uid))
            canvas.drawText(textobject)

        self.baseline -= 1.5*cm
        if invoice.get_settings():
            lines = 0
            canvas.setFont(self.FONT_NAME, 9)
            textobject = canvas.beginText(1.5*cm, self.baseline)
            for line in invoice.get_settings().info({"invoice": invoice}).split("\n"):
                lines += 1
                textobject.textLine(line.strip())
            canvas.drawText(textobject)
            self.baseline -= lines * .5 * cm

    def draw_items(self, invoice, canvas):
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
        table = Table(data, colWidths=[1.7*cm, 11*cm, 2.5*cm, 2.5*cm])
        table.setStyle([
            ('FONT', (0, 0), (-1, -1), self.FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])
        tw, th, = table.wrapOn(canvas, 15*cm, 19*cm)
        table.drawOn(canvas, 1.5*cm, self.baseline-th)
        self.baseline = -26*cm

    def draw_footer(self, invoice, canvas):
        """ Draws the invoice footer """
        if invoice.get_settings():
            textobject = canvas.beginText(1.5*cm, self.baseline)
            for line in invoice.get_settings().footer({"invoice": invoice}).split("\n"):
                textobject.textLine(line.strip())
            canvas.drawText(textobject)
