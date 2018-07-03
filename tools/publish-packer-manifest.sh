#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o verbose

aws s3api put-object \
    --bucket datawire-static-files \
    --key kubernautlet/packer-manifest.json \
    --body packer-manifest.json
