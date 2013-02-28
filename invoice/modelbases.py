from django.db import models


class Address(models.Model):

    contact_name = models.CharField(max_length=60)
    address_one = models.CharField(max_length=60)
    address_two = models.CharField(max_length=60)
    town = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=20)
