#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

#
# file: build-docker.sh
#
# Compiles the Kubernautlet into a Linux native binary using a Dockerized build environment.
#

apt-get update && apt-get install binutils make

# produce a copy of the host mount that we can safely modify for test / build etc without affecting the developers
# current tree
cp -R ${MOUNTDIR}/. .

make clean

pip install -Ur requirements/test.txt
pip install pyinstaller

if [[ "${SKIP_TESTS}" != "true" ]]; then
tox -e py36
fi

pyinstaller kubernaut/agent.py \
    --distpath "build/out" \
    --name ${BINARY_NAME} \
    --onefile \
    --workpath build

chown ${HOST_USER_ID}:${HOST_USER_GROUP_ID} build/out/${BINARY_NAME}

mkdir -p -m 755 ${MOUNTDIR}/build/out
cp build/out/${BINARY_NAME} ${MOUNTDIR}/build/out/

chown ${HOST_USER_ID}:${HOST_USER_GROUP_ID} ${MOUNTDIR}/build
chown -R ${HOST_USER_ID}:${HOST_USER_GROUP_ID} ${MOUNTDIR}/build/*
