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

exec_base_name="kubernaut-agent"
exec_full_name="${exec_base_name}_${os}_${platform}"

pyinstaller kubernaut/agent.py \
    --distpath build/dist \
    --name ${exec_full_name} \
    --onefile \
    --workpath build

ln -sf build/dist/${exec_full_name} build/dist/${exec_base_name}
