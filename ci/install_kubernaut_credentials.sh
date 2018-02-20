#!/usr/bin/env bash

openssl aes-256-cbc \
    -K $encrypted_7169b827dcd8_key \
    -iv $encrypted_7169b827dcd8_iv \
    -in ci/kubernaut.json.enc \
    -out ci/kubernaut.json \
    -d

mkdir -p ~/.config/kubernaut
mv ci/kubernaut.json ~/.config/kubernaut/config.json
