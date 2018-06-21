import os

import tempfile

from pathlib import Path
from kubernaut.kubernetes import kubeadm, kubectl
from kubernaut.agent import ClusterDetail


class Cluster:

    def __init__(self, cluster_id: str, state: str, kubeconfig: str, token: str):
        self.cluster_id = cluster_id
        self.state = state
        self.kubeconfig = kubeconfig
        self.token = token


    def shutdown(self):
        with tempfile.NamedTemporaryFile(encoding="UTF-8", prefix="kubeconfig-") as fp:
            fp.write(self.kubeconfig)
            env_kubectl = {"KUBECONFIG": os.getenv(fp.name)}

            (status, output) = kubectl(["get", "nodes", "--output=jsonpath={.items[*].metadata.name}"], env_kubectl)
            nodes = []
            if status == 0:
                nodes = output.split(" ")

            for name in nodes:
                kubectl(["drain", name, "--delete-local-data", "--force", "--ignore-daemonsets"], env_kubectl)
                kubectl(["delete", "node", name])

            # If we move to a world where there are multiple Kubernetes clusters handled by a single agent then this
            # code will need to be modified as the agent will not be installed per cluster most likely.
            kubeadm(["reset"])
            os.system("systemctl poweroff")
