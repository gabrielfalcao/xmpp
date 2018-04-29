# Config
OSNAME			:= $(shell uname)

ifeq ($(OSNAME), Linux)
OPEN_COMMAND		:= gnome-open
else
OPEN_COMMAND		:= open
endif

all: tests docs

SHELL			:= /bin/bash
PYTHONPATH		:= $(shell pwd)
PATH			:= $(PATH):$(shell pwd)
export PATH
export PYTHONPATH
export SHELL

tests: unit

# http://misc.flogisoft.com/bash/tip_colors_and_formatting

lint:
	@flake8 xmpp

clean:
	git clean -Xdf

unit:
	pipenv run nosetests --with-coverage --cover-erase \
	    --cover-package=xmpp.core \
	    --cover-package=xmpp.networking \
	    --cover-package=xmpp.stream \
	    --cover-package=xmpp.extensions \
	    --cover-package=xmpp.models \
	    --verbosity=2 -s --rednose tests/unit

functional:
	pipenv run nosetests -x --with-coverage --cover-erase \
	    --cover-package=xmpp \
	    --verbosity=2 -s --rednose --logging-clear-handlers \
	    tests/functional

continuous-integration: prepare tests

prepare: ensure-dependencies

fake-devices:
	for x in `seq 10`; do printf "HMSET device.`uuidgen | sed s,-,,g | awk '{print tolower($0)}'`.notification_window window 300 last_updated `date +%s`" | redis-cli; done

ensure-dependencies:
	@pipenv install --dev

release: tests docs
	@./.release
	@echo "publishing to pypi"
	@pipenv run python setup.py build sdist
	@pipenv run twine upload dist/*.tar.gz


list:
	@$(executable) list

html-docs:
	rm -rf docs/build
	cd docs && make doctest html

docs: html-docs

.PHONY: html-docs docs

component-presence-proxy:
	python examples/component-presence-proxy.py

echobot:
	pipenv run python examples/echobot.py

service-discovery:
	pipenv run python examples/service_discovery.py


presence-auto-subscriber:
	pipenv run python examples/presence-auto-subscriber.py
