#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Virtualenv not active! Abort!"
    exit 1
fi

echo "This is a tagged commit"
source vars.sh
