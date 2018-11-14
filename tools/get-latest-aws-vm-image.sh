#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
set -o verbose

wget -O /tmp/packer-manifest.json \
    https://s3.amazonaws.com/datawire-static-files/kubernautlet/packer-manifest.json

cat /tmp/packer-manifest.json | python -c 'import json,sys; obj=json.load(sys.stdin); print([x for x in obj["builds"] if x["builder_type"] == "amazon-ebs"][0]["artifact_id"].split(":")[1]);'
