from setuptools import setup

APP_NAME = "django-invoice"
VERSION = 0.3

setup(
    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    name=APP_NAME,
    version=VERSION,
    description='Pluggable django invoicing app',
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    install_requires=[
        "django>=1.3",
        "reportlab",
    ],
    modules=[
        'invoice',
        'invoice.management',
        'invoice.management.commands',
        'invoice.utils',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)
