import codecs
import os

from setuptools import setup, find_packages

APP_NAME = "django-invoice"
VERSION = __import__('invoice').get_version()

here = os.path.abspath(os.path.dirname(__file__))


def read(*files):
    content = ''
    for f in files:
        content += codecs.open(os.path.join(here, f), 'r').read()
    return content


setup(
    name=APP_NAME,
    version=VERSION,
    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django invoice pdf",
    description='Pluggable django invoicing app',
    long_description=read("README.rst"),
    install_requires=read('requirements/base.txt'),
    tests_require=read('requirements/qa.txt'),
    packages=find_packages(),
    license="GPL v3",
)
