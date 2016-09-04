from __future__ import absolute_import

import datetime
import os
import pytest

from invoice.models import Invoice


@pytest.mark.django_db
class TestInvoice:
    def test_get_due(self, invoice):
        assert Invoice.objects.get_due().count() == 1

        invoice.set_paid()
        assert Invoice.objects.get_due().count() == 0

    def test_get_due2(self, invoice):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        invoice.date_issuance = yesterday
        invoice.save()
        assert Invoice.objects.get_due().count() == 1

        invoice.date_issuance = tomorrow
        invoice.save()
        assert Invoice.objects.get_due().count() == 0

    def test_generate_file(self, invoice):
        basedir = "/tmp"
        if invoice.logo:
            assert os.path.exists(invoice.logo) is True
        filename = invoice.export_file(basedir)
        assert os.path.exists(filename) is True
        stats = os.stat(filename)
        # the file has to contain something
        assert stats.st_size > 10
        os.unlink(filename)
