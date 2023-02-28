WORKDIR = yatube
TEMPLATES-DIR = $(WORKDIR)/templates
MANAGE = python $(WORKDIR)/manage.py

run:
	$(MANAGE) runserver

migration:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

shell:
	$(MANAGE) shell

style:
	black -S -l 79 $(WORKDIR)/
	isort $(WORKDIR)
	djlint --reformat $(TEMPLATES-DIR)
	mypy $(WORKDIR)
	flake8 $(WORKDIR)

test_about:
	$(MANAGE) test about.tests

test_posts_forms:
	$(MANAGE) test posts.tests.test_forms

test_posts_models:
	$(MANAGE) test posts.tests.test_models

test_posts_urls:
	$(MANAGE) test posts.tests.test_urls

test_utils:
	$(MANAGE) test core

test_posts_views:
	$(MANAGE) test posts.tests.test_views
