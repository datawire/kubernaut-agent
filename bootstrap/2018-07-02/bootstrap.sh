#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o verbose

export INSTANCE_ID="$(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
export IP_ADDRESS="$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
export CLUSTER_NAME="$INSTANCE_ID"
export KUBERNETES_VERSION="$(cat /etc/kubernaut/kubernetes_version | tr -d '\n')"

aws ec2 create-tags \
   --resources $INSTANCE_ID \
   --region us-east-1 \
   --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=owned

# We needed to match the hostname expected by kubeadm to the hostname used by kubelet
#
# see: https://github.com/kubernetes/kubeadm/issues/584
#
FULL_HOSTNAME="$(curl -s http://169.254.169.254/latest/meta-data/hostname)"
hostname "$FULL_HOSTNAME"

# Start services
systemctl start docker
systemctl start kubelet

# Initialize the master
cat >/tmp/kubeadm.yaml <<EOF
---
apiVersion: kubeadm.k8s.io/v1alpha1
kind: MasterConfiguration
networking:
 podSubnet: 192.168.0.0/16
nodeName: $FULL_HOSTNAME
tokenTTL: "0"
cloudProvider: aws
kubernetesVersion: v$KUBERNETES_VERSION
apiServerCertSANs:
- $IP_ADDRESS
EOF

kubeadm reset
kubeadm init --config /tmp/kubeadm.yaml
rm /tmp/kubeadm.yaml

# Use the local kubectl config for further kubectl operations
export KUBECONFIG=/etc/kubernetes/admin.conf

# Allow all apps to run on master
kubectl taint nodes --all node-role.kubernetes.io/master-

# Allow load balancers to route to master
kubectl label nodes --all node-role.kubernetes.io/master-

# Install Calico
kubectl apply -f https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/rbac-kdd.yaml
kubectl apply -f https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calico-networking/1.7/calico.yaml

# Allow the user to act as administrator of the cluster
kubectl create clusterrolebinding admin-cluster-binding --clusterrole=cluster-admin --user=admin

# Prepare the kubectl config file for download to client (IP address)
export KUBECONFIG_OUTPUT=/tmp/kubeconfig_ip
kubeadm alpha phase kubeconfig user \
 --client-name admin \
 --apiserver-advertise-address $IP_ADDRESS \
 > ${KUBECONFIG_OUTPUT}

chown ubuntu:ubuntu ${KUBECONFIG_OUTPUT}
chmod 0600 ${KUBECONFIG_OUTPUT}
