SHELL = bash

.ONESHELL:
.PHONY: clean packer/packer-vars.json

SHELL_IMAGE = python:3.6-slim

GIT_MAIN_BRANCH ?= master
GIT_COMMIT_HASH := $(shell git rev-parse --short --verify HEAD)

DOCKER_RUN = docker run --rm -it --volume=$(PWD):/kubernaut-agent --workdir=/kubernaut-agent

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
	rm -rf build

compile: venv
	$(DOCKER_RUN) make venv \
		&& $(COMPILER_EXEC) kubernaut/cli.py \
    		--distpath build/out \
    		--name $(BINARY_NAME) \
    		--onefile \
    		--workpath build

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

venv: venv/bin/activate

venv/bin/activate: requirements.txt requirements/.
	test -d venv || virtualenv venv --python python3
	venv/bin/pip install -q -Ur requirements.txt
	touch venv/bin/activate

vm-images: packer/packer-vars.json
	$(PACKER_VALIDATE)
