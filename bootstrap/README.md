# Bootstrap Bundles

A bootstrap bundle is responsible for initializing a Kubernetes cluster on a virtual machine. The [bootstrap shim](shim.sh) is responsible for downloading and executing a bootstrap script that initializes the cluster machinery, installs add-ons / plugins and then starts the Kubernautlet.

# Directory Layout

Each subdirectory is a bundle. A bundle should contain an executable `bootstrap.sh` that can be invoked to perform cluster initialization.
