#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Virtualenv not active! Abort!"
    exit 1
fi

source vars.sh
pip install awscli

aws s3 cp \
    s3://${RELEASE_S3_BUCKET}/${EXECUTABLE_NAME}/${VERSION}/${OS}/${PLATFORM}/${EXECUTABLE_NAME} \
    s3://${RELEASE_S3_BUCKET}/${EXECUTABLE_NAME}/${TRAVIS_TAG}/${OS}/${PLATFORM}/${EXECUTABLE_NAME}
