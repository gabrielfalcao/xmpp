MAKEFILE_PATH		:= $(realpath $(firstword $(MAKEFILE_LIST)))
GIT_ROOT		:= $(shell dirname $(MAKEFILE_PATH))
VENV_ROOT		:= $(GIT_ROOT)/.venv

PACKAGE_NAME		:= xmpp
MAIN_CLI_NAME		:= xmpp
REQUIREMENTS_FILE	:= development.txt

PACKAGE_PATH		:= $(GIT_ROOT)/$(PACKAGE_NAME)
REQUIREMENTS_PATH	:= $(GIT_ROOT)/$(REQUIREMENTS_FILE)
MAIN_CLI_PATH		:= $(VENV_ROOT)/bin/$(MAIN_CLI_NAME)
export VENV		?= $(VENV_ROOT)

######################################################################
# Phony targets (only exist for typing convenience and don't represent
#                real paths as Makefile expects)
######################################################################



all: | $(MAIN_CLI_PATH)  # default target when running `make` without arguments

help:
	@egrep -h '^[^:]+:\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# creates virtualenv
venv: | $(VENV)

# updates pip3 and setuptools to their latest version
develop: | $(VENV)/bin/python3 $(VENV)/bin/pip

# installs the requirements and the package dependencies
setup: | $(MAIN_CLI_PATH)

# Convenience target to ensure that the venv exists and all
# requirements are installed
dependencies:
	@rm -f $(MAIN_CLI_PATH) # remove MAIN_CLI_PATH to trigger pip3 install
	$(MAKE) develop setup

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

lint:check-build
	@printf "\033[1;33mChecking for static errors...\033[0m"
	@find xmpp -name '*.py' | grep -v node | xargs flake8 --ignore=E501
	@printf "\r\033[1;37mChecking for static errors... \033[1;32mOK\033[0m\n"

check-build:
	@printf "\033[1;33mChecking if the build is working\033[0m..."
	@((python3 setup.py build 2>&1)2>&1>build.log) || (printf "\033[1;31mFAILED\r\n\n\033[0m\r" && cat build.log && echo "" && exit 1)
	@printf "\r\033[1;37mChecking if the build is working... \033[1;32mOK\033[0m\n"
	@rm -rf build*

clean:
	git clean -Xdf

unit:
	nosetests --with-coverage --cover-erase \
	    --cover-package=xmpp.core \
	    --cover-package=xmpp.networking \
	    --cover-package=xmpp.stream \
	    --cover-package=xmpp.extensions \
	    --cover-package=xmpp.models \
	    --verbosity=2 -s --rednose tests/unit

functional:
	nosetests -x --with-randomly --with-coverage --cover-erase \
	    --cover-package=xmpp \
	    --verbosity=2 -s --rednose --logging-clear-handlers \
	    tests/functional

continuous-integration: prepare tests

prepare: ensure-dependencies

fake-devices:
	for x in `seq 10`; do printf "HMSET device.`uuidgen | sed s,-,,g | awk '{print tolower($0)}'`.notification_window window 300 last_updated `date +%s`" | redis-cli; done

ensure-dependencies:
	@pip3 install -r development.txt

release: tests docs
	@./.release
	@echo "publishing to pypi"
	@python3 setup.py build sdist
	@twine upload dist/*.tar.gz


list:
	@$(executable) list

html-docs:
	rm -rf docs/build
	cd docs && make doctest html

docs: html-docs

.PHONY: html-docs docs

component-presence-proxy:
	python3 examples/component-presence-proxy.py

echobot:
	python3 examples/echobot.py

service-discovery:
	python3 examples/service_discovery.py


presence-auto-subscriber:
	python3 examples/presence-auto-subscriber.py


##############################################################
# Real targets (only run target if its file has been "made" by
#               Makefile yet)
##############################################################

# creates virtual env if necessary and installs pip3 and setuptools
$(VENV): | $(REQUIREMENTS_PATH)  # creates $(VENV) folder if does not exist
	echo "Creating virtualenv in $(VENV_ROOT)" && python3 -mvenv $(VENV)

# installs pip3 and setuptools in their latest version, creates virtualenv if necessary
$(VENV)/bin/python3 $(VENV)/bin/pip: # installs latest pip
	@test -e $(VENV)/bin/python3 || $(MAKE) $(VENV)
	@test -e $(VENV)/bin/pip3 || $(MAKE) $(VENV)
	@echo "Installing latest version of pip3 and setuptools"
	@$(VENV)/bin/pip3 install -U pip3 setuptools

 # installs latest version of the "black" code formatting tool
$(VENV)/bin/black: | $(VENV)/bin/pip
	$(VENV)/bin/pip3 install -U black

# installs this package in "edit" mode after ensuring its requirements are installed

$(VENV)/bin/nosetests $(MAIN_CLI_PATH): | $(VENV) $(VENV)/bin/pip3 $(VENV)/bin/python3 $(REQUIREMENTS_PATH)
	$(VENV)/bin/pip3 install -r $(REQUIREMENTS_PATH)
	$(VENV)/bin/pip3 install -e .

# ensure that REQUIREMENTS_PATH exists
$(REQUIREMENTS_PATH):
	@echo "The requirements file $(REQUIREMENTS_PATH) does not exist"
	@echo ""
	@echo "To fix this issue:"
	@echo "  edit the variable REQUIREMENTS_NAME inside of the file:"
	@echo "  $(MAKEFILE_PATH)."
	@echo ""
	@exit 1

###############################################################
# Declare all target names that exist for convenience and don't
# represent real paths, which is what Make expects by default:
###############################################################

.PHONY: \
	all \
	black \
	build-release \
	clean \
	dependencies \
	develop \
	push-release \
	release \
	setup \
	run \
	tests \
	unit \
	functional

.DEFAULT_GOAL	:= help
