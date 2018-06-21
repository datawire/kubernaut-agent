#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

#
# file: build-docker.sh
#
# Compiles the Kubernautlet into a Linux native binary using a Dockerized build environment.
#

apt-get update && apt-get install binutils make

# produce a copy of the host mount that we can safely modify for test / build etc without affecting the developers
# current tree
cp -R /mnt/project/. .

make clean

pip install -Ur requirements/test.txt
pip install pyinstaller

if [[ "${SKIP_TESTS}" != "true" ]]; then
tox -e py36
fi

pyinstaller kubernaut/cli.py \
    --distpath "build/out" \
    --name ${BINARY_NAME} \
    --onefile \
    --workpath build

mkdir -p ${MOUNT_DIR}/build/out
chown 1000:1000 ${MOUNT_DIR}/build/out build/out/${BINARY_NAME}
cp build/out/${BINARY_NAME} ${MOUNT_DIR}/build/out/
