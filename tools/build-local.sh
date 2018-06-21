#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

#
# file: build-local.sh
#
# Compiles the Kubernautlet into a native binary using the local environment. This is required if you want to create a
# Kubernautlet that can run on macOS or Windows
#