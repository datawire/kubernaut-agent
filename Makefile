SHELL = bash

.PHONY: clean compile venv packer packer/packer-vars.json test vm-images

GIT_MAIN_BRANCH ?= master
GIT_COMMIT_HASH := $(shell git rev-parse --short --verify HEAD)

DOCKER_IMAGE    = python:3.6-slim
DOCKER_MOUNTDIR = /project
DOCKER_WORKDIR  = $(DOCKER_MOUNTDIR)

override DOCKER_ARGS += --rm \
	-it \
	--volume=$(PWD):$(DOCKER_MOUNTDIR) \
	--workdir=$(DOCKER_WORKDIR) \
	-e MOUNTDIR=$(DOCKER_MOUNTDIR) \
	-e HOST_USER_ID=$(shell id -u) \
	-e HOST_USER_GROUP_ID=$(shell id -g) \

DOCKER_RUN      = docker run $(DOCKER_ARGS) $(DOCKER_IMAGE)

PACKER_IMAGE    = hashicorp/packer:light
PACKER_EXEC     = $(DOCKER_RUN)
PACKER_VARS     = packer/packer-vars.json
PACKER_TEMPLATE = packer/packer.json
override PACKER_ARGS += -var-file=$(PACKER_VARS)
PACKER_VALIDATE = $(PACKER_EXEC) validate $(PACKER_ARGS) $(PACKER_TEMPLATE)
PACKER_BUILD    = $(PACKER_EXEC) build $(PACKER_ARGS) $(PACKER_TEMPLATE)

BINARY_BASENAME := kubernautlet
BINARY_OS       := linux
BINARY_PLATFORM := x86_64
BINARY_NAME     := $(BINARY_BASENAME)-$(GIT_COMMIT_HASH)-$(BINARY_OS)-$(BINARY_PLATFORM)

clean:
	rm -rf \
		build \
		venv \
		.tox \
		*.egg-info \
		__pycache__ \
		.pytest_cache \
		ci-secrets.tar.gz
	find -iname "*.pyc" -delete

compile: SKIP_TESTS = false
compile: DOCKER_WORKDIR = /work
compile: DOCKER_ARGS += -e BINARY_NAME=$(BINARY_NAME)
compile: DOCKER_ARGS += -e SKIP_TESTS=$(SKIP_TESTS)
compile:
	$(DOCKER_RUN) $(DOCKER_MOUNTDIR)/tools/build-docker.sh
	cp build/out/$(BINARY_NAME) build/out/$(BINARY_BASENAME)

packer/packer-vars.json:
	tools/create-packer-vars.sh $(GIT_COMMIT_HASH) $(BINARY_NAME)

packer: DOCKER_IMAGE=$(PACKER_IMAGE)
packer: shell

shell: DOCKER_ARGS += --entrypoint=/bin/bash
shell: DOCKER_WORKDIR=$(DOCKER_MOUNTDIR)
shell:
	$(DOCKER_RUN)

test: DOCKER_WORKDIR = /work
test:
	$(DOCKER_RUN) $(DOCKER_MOUNTDIR)/tools/test-docker.sh

venv: venv/bin/activate

venv/bin/activate: requirements.txt requirements/
	test -d venv || virtualenv venv --python python3
	venv/bin/pip install -q -Ur requirements.txt
	venv/bin/pip install -q -Ur requirements/dev.txt
	touch venv/bin/activate

vm-images: DOCKER_IMAGE = hashicorp/packer:light
vm-images: DOCKER_ARGS += -e GOOGLE_APPLICATION_CREDENTIALS=/root/google-cloud/credentials.json
vm-images: DOCKER_ARGS += -v ~/.aws:/root/.aws -v ~/google-cloud:/root/google-cloud
vm-images: PACKER_ARGS += -machine-readable
vm-images: packer/packer-vars.json
	@$(PACKER_VALIDATE)
	@$(PACKER_BUILD)
