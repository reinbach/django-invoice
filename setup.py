from setuptools import setup

APP_NAME = "django-invoice"
VERSION = 0.3

setup(
    name=APP_NAME,
    version=VERSION,
    description='Pluggable django invoicing app',
    packages=[
        'invoice',
        'invoice.utils'
    ],

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    licence="GPL v3",
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django invoice pdf",

    install_requires=[
        "django>=1.3",
        "reportlab",
    ],
)
