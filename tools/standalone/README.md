# Kubernaut Standalone

Launches a standalone Kubernaut virtual machine. This is primarily useful for development, debugging and testing.

# Usage

**NOTE** This currently only supports standalone provisioning on Amazon Web Services.

## Create a standalone instance:

`make standalone`

If you want to use a specific virtual machine image then you should override the `AWS_IMAGE_ID` variable:

`make standalone AWS_IMAGE_ID=ami-abcdef123`

## Delete a standalone instance:

`make cleanup`

## SSH into the underlying VM:

Useful for debugging or developing bootstrap scripts without continually pulling an instance up or down.

`make ssh`
