from django.db.models.signals import post_syncdb
from django.dispatch import receiver

from invoice import models
from invoice import test_data


@receiver(post_syncdb, sender=models)
def load_test_data(sender, **kwargs):
    test_data.load()
