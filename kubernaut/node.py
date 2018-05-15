import os

from pathlib import Path
from kubernaut.kubernetes import kubeadm, kubectl


def shutdown():
    env_kubectl = {}
    if os.getenv("KUBECONFIG"):
        env_kubectl = {"KUBECONFIG": os.getenv("KUBECONFIG")}
    else:
        env_kubectl = {"KUBECONFIG": os.path.expanduser(str((Path.home() / ".kube" / "config")))}

    (status, output) = kubectl(["get", "nodes", "--output=jsonpath={.items[*].metadata.name}"], env_kubectl)
    nodes = []
    if status == 0:
        nodes = output.split(" ")

    for name in nodes:
        kubectl(["drain", name, "--delete-local-data", "--force", "--ignore-daemonsets"], env_kubectl)
        kubectl(["delete", "node", name])

    kubeadm(["reset"])
    os.system("systemctl poweroff")
