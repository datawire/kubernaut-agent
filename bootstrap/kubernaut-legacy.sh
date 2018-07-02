#!/bin/bash

set -o verbose
set -o errexit
set -o pipefail

export INSTANCE_ID="$(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
export KUBEADM_TOKEN="${kubeadm_token}"
export DNS_NAME="${dns_name}"
export IP_ADDRESS="$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
export CLUSTER_NAME="$INSTANCE_ID"
export KUBERNETES_VERSION="$(cat /etc/kubernaut/kubernetes_version | tr -d '\n')"

set -o nounset

aws ec2 create-tags \
   --resources $INSTANCE_ID \
   --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=owned

# We needed to match the hostname expected by kubeadm to the hostname used by kubelet
#
# see: https://github.com/kubernetes/kubeadm/issues/584
#
FULL_HOSTNAME="$(curl -s http://169.254.169.254/latest/meta-data/hostname)"
hostname "$FULL_HOSTNAME"

# Make DNS lowercase
DNS_NAME=$(echo "$DNS_NAME" | tr 'A-Z' 'a-z')

# Start services
systemctl start docker
systemctl start kubelet

# Initialize the master
cat >/tmp/kubeadm.yaml <<EOF
---
apiVersion: kubeadm.k8s.io/v1alpha1
kind: MasterConfiguration
nodeName: $FULL_HOSTNAME
token: $KUBEADM_TOKEN
tokenTTL: "0"
cloudProvider: aws
kubernetesVersion: v$KUBERNETES_VERSION
apiServerCertSANs:
- $DNS_NAME
- $IP_ADDRESS
EOF

kubeadm reset
kubeadm init --config /tmp/kubeadm.yaml
rm /tmp/kubeadm.yaml

# Use the local kubectl config for further kubectl operations
export KUBECONFIG=/etc/kubernetes/admin.conf

# Install calico
kubectl apply -f /tmp/calico.yaml

# Allow all apps to run on master
kubectl taint nodes --all node-role.kubernetes.io/master-

# Allow load balancers to route to master
kubectl label nodes --all node-role.kubernetes.io/master-

# Allow the user to administer the cluster
kubectl create clusterrolebinding admin-cluster-binding --clusterrole=cluster-admin --user=admin

# Prepare the kubectl config file for download to client (IP address)
export KUBECONFIG_OUTPUT=/home/ubuntu/kubeconfig_ip
kubeadm alpha phase kubeconfig user \
 --client-name admin \
 --apiserver-advertise-address $IP_ADDRESS \
 > $KUBECONFIG_OUTPUT
chown ubuntu:ubuntu $KUBECONFIG_OUTPUT
chmod 0600 $KUBECONFIG_OUTPUT

# Export Kubeconfig to S3
aws s3api put-object \
    --bucket kubernaut-io-v1 \
    --key instances/$INSTANCE_ID/kubeconfig \
    --body "$KUBECONFIG_OUTPUT"

# Mark the instance as unclaimed
aws ec2 create-tags \
    --resources $INSTANCE_ID \
    --tags Key=io.kubernaut/Status,Value=unclaimed
