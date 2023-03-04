WORKDIR = yatube
TEMPLATES-DIR = $(WORKDIR)/templates
MANAGE = python $(WORKDIR)/manage.py
TESTS = $(WORKDIR)/posts/tests

run:
	$(MANAGE) runserver

migration:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

shell:
	$(MANAGE) shell

style:
	black $(WORKDIR)/
	isort $(WORKDIR)
	djlint --reformat $(TEMPLATES-DIR)

check:
	mypy $(WORKDIR)
	flake8 $(WORKDIR)

test:
	$(MANAGE) test --keepdb $(TESTS)
