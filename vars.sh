#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID="AKIAJMWHHLPPAAFZSNSA"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_DEFAULT_OUTPUT="json"

export EXECUTABLE_NAME="kubernaut-agent"
export OS="$(uname | tr [:upper:] [:lower:])"
export PLATFORM="$(uname -m | tr [:upper:] [:lower:])"
export VERSION="$(git rev-parse --short HEAD)"

export RELEASE_S3_BUCKET="datawire-static-files"
export RELEASE_S3_KEY="$EXECUTABLE_NAME/$VERSION/$OS/$PLATFORM/$EXECUTABLE_NAME"
