import os

import tempfile

from pathlib import Path
from kubernaut.kubernetes import kubeadm, kubectl


def shutdown(cluster):
    with tempfile.NamedTemporaryFile(encoding="UTF-8", prefix="kubeconfig-") as fp:
        fp.write(cluster.kubeconfig)
        env_kubectl = {"KUBECONFIG": os.getenv(fp.name)}

        (status, output) = kubectl(["get", "nodes", "--output=jsonpath={.items[*].metadata.name}"], env_kubectl)
        nodes = []
        if status == 0:
            nodes = output.split(" ")

        for name in nodes:
            kubectl(["drain", name, "--delete-local-data", "--force", "--ignore-daemonsets"], env_kubectl)
            kubectl(["delete", "node", name])

        kubeadm(["reset"])
        os.system("systemctl poweroff")
