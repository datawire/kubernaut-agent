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

os="$(uname | tr [:upper:] [:lower:])"
platform="$(uname -m | tr [:upper:] [:lower:])"

executable_name="kubernaut-agent_${os}_${platform}"

pyinstaller kubernaut/agent.py \
    --distpath build/dist \
    --name ${executable_name} \
    --onefile \
    --workpath build
