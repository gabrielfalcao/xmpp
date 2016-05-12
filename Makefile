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

tests: lint unit functional

# http://misc.flogisoft.com/bash/tip_colors_and_formatting

lint:check-build
	@printf "\033[1;33mChecking for static errors...\033[0m"
	@find xmpp -name '*.py' | grep -v node | xargs flake8 --ignore=E501
	@printf "\r\033[1;37mChecking for static errors... \033[1;32mOK\033[0m\n"

check-build:
	@printf "\033[1;33mChecking if the build is working\033[0m..."
	@((python setup.py build 2>&1)2>&1>build.log) || (printf "\033[1;31mFAILED\r\n\n\033[0m\r" && cat build.log && echo "" && exit 1)
	@printf "\r\033[1;37mChecking if the build is working... \033[1;32mOK\033[0m\n"
	@rm -rf build*

clean:
	git clean -Xdf

unit:
	nosetests --with-coverage --cover-erase \
	    --cover-package=xmpp \
	    --verbosity=2 -s --rednose tests/unit

functional:
	nosetests -x --with-randomly --with-coverage --cover-erase \
	    --cover-package=xmpp \
	    --verbosity=2 -s --rednose --logging-clear-handlers \
	    tests/functional

tests: unit functional

continuous-integration: prepare tests

prepare: ensure-dependencies

fake-devices:
	for x in `seq 10`; do printf "HMSET device.`uuidgen | sed s,-,,g | awk '{print tolower($0)}'`.notification_window window 300 last_updated `date +%s`" | redis-cli; done

ensure-dependencies:
	@pip install -r development.txt

release: tests docs
	@./.release

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
	python examples/echobot.py

service-discovery:
	python examples/service_discovery.py


presence-auto-subscriber:
	python examples/presence-auto-subscriber.py
