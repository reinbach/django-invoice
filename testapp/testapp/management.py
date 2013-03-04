from django.db.models.signals import post_syncdb
from invoice import test_data, models


def load_test_data(sender, **kwargs):
    test_data.load()

post_syncdb.connect(load_test_data, sender=models)
