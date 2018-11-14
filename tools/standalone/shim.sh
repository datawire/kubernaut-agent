#!/usr/bin/env bash

# Copyright 2018 Datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

# shim.sh
#
# The bootstrap shim executes when an instance is launched. It downloads a bootstrap archive from a remote location and
# then executes a script named 'bootstrap-kubernaut' contained in the archive.
#
# The shim makes it possible to perform on-launch configuration of an instance rather than bake all the configuration
# right into the VM image.
#

set -o errexit
set -o pipefail
set -o verbose

BOOTSTRAP_SCRIPT="bootstrap.sh"
BOOTSTRAP_VARS="/tmp/bootstrap.vars"
source ${BOOTSTRAP_VARS}

if [[ -z "${BOOTSTRAP_REPO}" ]]; then
    printf "%s\n" "WARN : Bootstrap process skipped because BOOTSTRAP_REPO is unset or empty"
    exit 0
fi

cd /tmp
git clone ${BOOTSTRAP_REPO} kubernaut-agent-bootstrap
cd kubernaut-agent-bootstrap/${BOOTSTRAP_BUNDLE}

if [[ ! -f "${BOOTSTRAP_SCRIPT}" ]]; then
    printf "%s\n" "ERROR: Bootstrap process cannot continue. Missing bootstrap.sh in ${BOOTSTRAP_REPO} -> ${BOOTSTRAP_BUNDLE}"
    exit 1
fi

chmod +x ${BOOTSTRAP_SCRIPT}
./${BOOTSTRAP_SCRIPT}
