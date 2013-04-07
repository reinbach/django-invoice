from django.db.models.signals import post_syncdb
from django.dispatch import receiver
import invoice


@receiver(post_syncdb, sender=invoice.models)
def test_data(sender, **kwargs):
    invoice.test_data.load()
