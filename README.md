# Django Invoice

General purpose invoicing app. Based on hard work of
Simon Luijk [https://github.com/simonluijk/django-invoice]

This app provides only base model of an invoice with exporting abilities
to PDF format. Model is fully configurable (swappable `contractor` and `subscriber` types).
The exporter to PDF is open for extension. The current look of an exported invoice you
can see below. The tests generates one anyway, so you can  try on your own.
