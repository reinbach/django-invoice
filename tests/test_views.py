import pytest

from django.core.urlresolvers import reverse


@pytest.mark.django_db
class TestDownload:
    def test_view(self, invoice, client):
        response = client.get(reverse("invoice", args=[invoice.uid]))
        assert response.status_code == 200
        attachment = 'attachment; filename="{0}"'.format(invoice.filename)
        assert response['Content-Disposition'] == attachment

    def test_not_found(self, client):
        response = client.get(reverse("invoice", args=["wrong"]))
        assert response.status_code == 404
