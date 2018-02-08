# Release Process

The publish process for Kubernaut Agent is manual but the rules are simple:

- The following are **NEVER** published:
    - branch builds other than `master`.
    - pull request builds.
    - failed builds on any branch.

- If the build is `master` then the successful built and tested artifact is published with a short git hash.
- If the build is a tag from `master` then the artifact published for the tagged commit is found and re-published as the tag name.

- An untagged publish from `master` is known as pre-release software.
- A tagged publish from `master` is known as General Availability (GA).

# Publish Location

The binaries are published into the `datawire-static-files` S3 bucket.

# Publish Script

The code that handles publishing releases is located in [publish.sh](publish.sh)
