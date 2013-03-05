:author: Tomas Peterka & Simon Luijk

Django Invoice (currently unstable)
===================================

General purpose invoicing app.

This app provides simple (but sufficient) Invoice model with export abilities.
The default export is into PDF but it's easy to write and use your own. The app is 
python 3 comptibilite, has full unicode fonts and ability to use company logo.

The model provides an option to use your own Address model via setting `INVOICE_ADDRESS_MODEL`
and Bank Account model via `INVOICE_BANK_ACCOUNT_MODEL`. Both settings the has to be a string
with full class name (e.g. "myproject.core.models.CompanyInformation").
The only rule for custom models is that it has to have a method `as_text` which returns unicode 
string with newline separators `\n`. Addresses will be used as contractor and subscriber. 

If BankAccount reference is presented, then it will be rendered below contractor information. Bellow bank
account information will be rendered *Variable symbol: {{ invoice.uid }}*. Please make sure that
you provide an numerical identifier when creating an invoice. Some random stuff will be generated
otherwise.

The invoice is intended to be referenced via foreign key from another model which handles
access policy and payments. These mechanisms are not provided in this app in favor for its
generality.

Invoice has some interesting methods:

**invoice.export_bytes()** - returns bytes of rendered invoice

**invoice.export_response()** - returns HttpResponse with the invoice as an attachment

**invoice.export_file(basedir)** - saves the invoice into a file in basedir and returns absolute path to the file

**invoice.export_attachment()** - returns MIMEApplication usable in email ::

    email = EmailMessage(to=[email, ], subject="Invoice", text="Hello")
    email.atttach(invoice.export_attachment())
    email.send()

Here we provide an example invoice generated from test

.. image:: example.png
    :align: right
    :class: float-right




Export module
-------------

Provides base for Export class and PDFExport class which is the default 
export class in Invoice model. There is possibility to write your own exporter
and then simply use it within Invoice ::

    from myproject import MyExporter
    
    order = MyOrder.objects.get(pk=1)
    order.invoice.export = MyExporter()

    email = EmailMessage(to=[email, ], subject="Invoice", text="Hello")
    email.attach(order.invoice.export_attachment())
    email.send()



TestApp
-------
For running you need just django, reportlab and PIL installed.

You can try example project using the Invoices. There is currently only admin interface
which allows you to try to make your own InvoiceSetting and export invoice PDF from it
via admin action.

You can run tests from this example app. You can run the test via ::

    python manage.py test invoice

