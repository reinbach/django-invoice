BUILDDIR = build
PROJECT = invoice

help:
	@echo 'Makefile for django-invoice                                        '
	@echo '                                                                   '
	@echo 'Usage:                                                             '
	@echo '   make develop                     setup development environment  '
	@echo '   make checks                      run pep8/flake8 checks         '
	@echo '   make test                        run tests                      '
	@echo '                                                                   '


mkbuilddir:
	@mkdir -p ${BUILDDIR}


develop:
	@pip install -U pip
	@pip install -qr requirements/base.txt
	@pip install -qr requirements/qa.txt
	@pip install -e .


checks:
	@pep8 invoice testapp tests || true
	@flake8 invoice testapp tests || true


test:
	@py.test --cov-config .coveragerc --cov-report html --cov-report term \
	--cov=invoice || true
