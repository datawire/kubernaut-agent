#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

#
# file: publish.sh
#
# More information is documented in the RELEASE.md file at repository root.
#

echo "This is NOT a tagged commit"
source vars.sh

branch="${TRAVIS_BRANCH:?TRAVIS_BRANCH envionment variable is not set}"
tag="${TRAVIS_TAG}"


if [[ "$TRAVIS_PULL_REQUEST" -ne "false" ]]; then is_pr="true";  else is_pr="false"; fi
if [[ -n "$TRAVIS_TAG" ]];                   then is_tag="true"; else is_tag="false"; fi

echo "Branch       = '$branch'"
echo "Version      = '$VERSION'"
echo "Pull Request = '$is_pr'"
echo "Is Tag       = '$is_tag'"
echo "Tag          = '$tag'"
echo "S3 Bucket    = '$RELEASE_S3_BUCKET'"
echo "S3 Object    = '$RELEASE_S3_KEY'"

#mkdir ~/.aws
#cp ci/aws_config ~/.aws/config
#
#aws s3api put-object \
#    --bucket "$RELEASE_S3_BUCKET" \
#    --key "$RELEASE_S3_KEY" \
#    --body "build/dist/$VERSION/$OS/$PLATFORM"
