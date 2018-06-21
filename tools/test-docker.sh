#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

apt-get update && apt-get install make

# produce a copy of the host mount that we can safely modify for test / build etc without affecting the developers
# current tree
cp -R /mnt/project/. .

make clean

pip install -Ur requirements/test.txt
tox -e py36
