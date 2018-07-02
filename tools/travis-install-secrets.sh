#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# =============================================================================
# Note: This script only does something meaningful when run from TravisCI
# =============================================================================

TRAVIS="${TRAVIS:-false}"

if [[ "${TRAVIS}" != "true" ]]; then
    printf "Error: This script can only be run from inside TravisCI\n"
    exit 1
fi

openssl aes-256-cbc \
    -K $encrypted_7169b827dcd8_key \
    -iv $encrypted_7169b827dcd8_iv \
    -in ci-secrets.tar.gz.enc \
    -out ci-secrets.tar.gz \
    -d

tar -xvf ci-secrets.tar.gz

mkdir -p ~/.aws
mv ci-secrets/aws_config ~/.aws/config
mv ci-secrets/aws_credentials ~/.aws/credentials

mkdir -p ~/googlecloud
mv ci-secrets/googlecloud/credentials.json ~/googlecloud/credentials.json

rm -f ci-secrets.tar.gz
