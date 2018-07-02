#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# travis-create-secrets.sh
#
# Creates a Gzipped tarball containing multiple secrets for use when running on Travis CI.

secrets_dir="ci-secrets"

if [[ ! -d ${secrets_dir} ]]; then
    printf "Please create a directory {PROJECT_ROOT}/ci-secrets"
    exit 1
fi

rm -f ci-secrets.tar.gz
tar -zcvf ci-secrets.tar.gz ci-secrets
travis encrypt-file ci-secrets.tar.gz ci-secrets.tar.gz.enc --force
