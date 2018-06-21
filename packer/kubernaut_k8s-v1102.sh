#!/usr/bin/env bash
set -o verbose
set -o errexit
set -o pipefail

export DEBIAN_FRONTEND=noninteractive
export KUBERNETES_VERSION="1.10.2"
export KUBERNETES_VERSION_DEB="${KUBERNETES_VERSION}-00"

set -o nounset

# --- Distribution Upgrade ---

apt-get update
apt-get \
    -y \
    -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" \
    dist-upgrade

apt-get -y install \
    apt-transport-https \
    awscli \
    ca-certificates \
    curl \
    software-properties-common

rm -rf /var/lib/apt/lists/*

# --- Docker Installation ---

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update
apt-get -y install docker-ce

rm -rf /var/lib/apt/lists/*

systemctl stop docker
systemctl enable docker

# --- Kubernetes Installation ---

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF

apt-get update
apt-get -y install \
	kubelet=${KUBERNETES_VERSION_DEB} \
	kubeadm=${KUBERNETES_VERSION_DEB} \
	kubectl=${KUBERNETES_VERSION_DEB}

rm -rf /var/lib/apt/lists/*

systemctl stop kubelet
systemctl disable kubelet

# --- Kubernaut Stuff ---
chmod +x /usr/local/bin/kubernaut-agent
mkdir /etc/kubernaut
printf "${KUBERNETES_VERSION}" > /etc/kubernaut/kubernetes_version
