SHELL = bash

.ONESHELL:
.PHONY: clean venv packer/packer-vars.json

SHELL_IMAGE = python:3.6-slim

GIT_MAIN_BRANCH ?= master
GIT_COMMIT_HASH := $(shell git rev-parse --short --verify HEAD)

DOCKER_MOUNT_POINT=/mnt/project
DOCKER_WORKDIR=/work

DOCKER_RUN_ARGS = --rm -it --volume=$(PWD):/mnt/project --workdir=/work
DOCKER_RUN = docker run $(DOCKER_RUN_ARGS) $(SHELL_IMAGE)

COMPILER_EXEC = pyinstaller

PACKER_EXEC=$(DOCKER_RUN) hashicorp/packer:light
PACKER_VARS=packer/packer-vars.json
PACKER_TEMPLATE=packer/packer.json
PACKER_VALIDATE=$(PACKER_EXEC) validate --var-file=$(PACKER_VARS) $(PACKER_TEMPLATE)
PACKER_BUILD=$(PACKER_EXEC) build --var-file=$(PACKER_VARS) $(PACKER_TEMPLATE)

BINARY_BASENAME := kubernautlet
BINARY_OS := linux
BINARY_PLATFORM := x86_64
BINARY_NAME := $(BINARY_BASENAME)-$(GIT_COMMIT_HASH)-$(BINARY_OS)-$(BINARY_PLATFORM)

clean:
	rm -rf build venv .[a-zA-Z_]*
	find -iname "*.pyc" -delete

compile: DOCKER_RUN_ARGS += -e BINARY_NAME=$(BINARY_NAME) -e MOUNT_DIR=$(DOCKER_MOUNT_POINT)
compile:
	$(DOCKER_RUN) $(DOCKER_MOUNT_POINT)/tools/build-docker.sh
	ln -sf build/out/$(BINARY_NAME) build/out/$(BINARY_BASENAME)

packer/packer-vars.json:
	-cat <<- EOF > $@
	{
		"commit": "$(GIT_COMMIT_HASH)",
		"forge_deregister": "false"
	}
	EOF

shell:
	docker run \
	-it \
	-w /app \
	-v $(PWD):/app \
	--rm $(SHELL_IMAGE) /bin/bash

test: venv
	venv/bin/tox -e py36

venv: venv/bin/activate

venv/bin/activate: requirements.txt requirements/
	test -d venv || virtualenv venv --python python3
	venv/bin/pip install -q -Ur requirements.txt
	venv/bin/pip install -q -Ur requirements/dev.txt
	touch venv/bin/activate

vm-images: packer/packer-vars.json
	$(PACKER_VALIDATE)
