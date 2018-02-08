#!/usr/bin/env bash

#
# file: build.sh
#
# Produces an Operating System and Platform specific single file executables. This needs to be run on each desired
# platform.
#
# Not tested with Windows or macOS.
#

set -euxo pipefail

source vars.sh

pyinstaller kubernaut/agent.py \
    --distpath "build/dist/$VERSION/$OS/$PLATFORM" \
    --name "${EXECUTABLE_NAME}" \
    --onefile \
    --workpath build

build/dist/${VERSION}/${OS}/${PLATFORM}/${EXECUTABLE_NAME} --help
