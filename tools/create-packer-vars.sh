#!/usr/bin/env bash
set -o errexit
set -o pipefail

GIT_COMMIT_HASH=${1:?not set or empty}
BINARY_NAME=${2:?not set or empty}

cat << EOF > packer/packer-vars.json
{
	"commit": "${GIT_COMMIT_HASH}",
	"forge_deregister": "false",
	"kubernautlet_binary_name": "${BINARY_NAME}"
}
EOF