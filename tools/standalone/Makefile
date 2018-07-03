# tools/standalone/Makefile

.PHONY: cleanup plan standalone init ssh terraform.tfvars.tpl

SHELL = /bin/bash

DOCKER_MOUNTDIR = /project
DOCKER_WORKDIR  = $(DOCKER_MOUNTDIR)

CLOUD=aws
CLOUD_VM_IMAGE=$(shell ../get-latest-$(CLOUD)-vm-image.sh)

override DOCKER_ARGS += --rm \
	-it \
	-u $(shell id -u):$(shell id -g) \
	--volume=$(CURDIR):$(DOCKER_MOUNTDIR) \
	--volume ~/.aws:/.aws \
	--volume ~/google-cloud:/google-cloud \
	--workdir=$(DOCKER_WORKDIR) \
	-e MOUNTDIR=$(DOCKER_MOUNTDIR) \
	-e HOST_USER_ID=$(shell id -u) \
	-e HOST_USER_GROUP_ID=$(shell id -g) \

DOCKER_RUN = docker run $(DOCKER_ARGS)

TF_IMAGE = hashicorp/terraform:light
TF_INIT = $(DOCKER_RUN) $(TF_IMAGE) init -get -upgrade

TF_PLANARGS = -out tfplan
TF_PLAN = $(DOCKER_RUN) $(TF_IMAGE) plan $(TF_PLANARGS)

TF_APPLY = $(DOCKER_RUN) $(TF_IMAGE) apply tfplan
TF_VALIDATE = $(DOCKER_RUN) $(TF_IMAGE) validate
TF_OUTPUT = $(DOCKER_RUN) $(TF_IMAGE) output $(TF_OUTPUT_VAR)

terraform.tfvars.tpl: CLUSTER_NAME=kubernaut-$(USER)
terraform.tfvars.tpl:
	sed -e "s/__IMAGE_ID__/$(CLOUD_VM_IMAGE)/g;s/__CLUSTER_NAME__/$(CLUSTER_NAME)/g" < terraform.tfvars.tpl > terraform.tfvars

terraform-shell: DOCKER_ARGS += --entrypoint=/bin/sh
terraform-shell:
	$(DOCKER_RUN) $(TF_IMAGE)

init:
	$(TF_INIT)

plan: terraform.tfvars.tpl init
	$(TF_PLAN)

cleanup: TF_PLANARGS += -destroy
cleanup: init plan
	$(TF_APPLY)

standalone: init plan validate
	$(TF_APPLY)

validate: init
	$(TF_VALIDATE)

ssh: TF_OUTPUT_VAR=instance_public_ip
ssh:
	ssh -i insecure_rsa ubuntu@$(shell $(TF_OUTPUT))

get-kubeconfig: CLUSTER_NAME=kubernaut-$(USER)
get-kubeconfig: TF_OUTPUT_VAR=instance_public_ip
get-kubeconfig:
	scp -i insecure_rsa ubuntu@$(shell $(TF_OUTPUT)):/tmp/kubeconfig_ip ~/.kube/$(CLUSTER_NAME)