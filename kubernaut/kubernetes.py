import typing
import json
import os
import sys

from pathlib import Path
from subprocess import run, STDOUT, PIPE
from typing import List, Mapping, Tuple


def find_kubectl(search: List[str] = None) -> str:
    for p in search:
        p = Path(p)
        p = p / "kubectl"
        if p.is_file() and os.access(str(p), os.X_OK):
            return str(p)

    raise ValueError("Unable to find `kubectl` program on system")


def read_kubeconfig(kubeconfig_file: Path) -> str:
    return kubeconfig_file.read_text(encoding="UTF-8")


def discover_cluster_id(namespace: str = "kube-system", kubeconfig: Path = (Path.home() / ".kube" / "config")) -> str:

    """Gets a Kubernetes cluster ID.

    Kubernetes as of v1.9.x does not have an official concept of cluster
    identity, however, the agent considers the UID of a namespace argument to be
    the canonical ID. Selection of the namespace is important however.

    :argument namespace the namespace to retrieve the UID from.
    :argument kubeconfig the path to the kubeconfig file to use.

    :return: the given namespaces UID acting as cluster ID.
    """

    env_kubectl = {}
    if os.getenv("KUBECONFIG"):
        env_kubectl = {"KUBECONFIG": os.getenv("KUBECONFIG")}
    else:
        env_kubectl = {"KUBECONFIG": os.path.expanduser(str(kubeconfig))}

    (status, output) = kubectl(args=["get", "namespace", namespace, "--output=json"], env=env_kubectl)
    if status == 0:
        return json.loads(output)["metadata"]["uid"]
    else:
        raise ValueError("Get namespace 'name = {}' failed 'exitcode = {}'", namespace, status)


def kubectl(args: List[str], env: Mapping[str, str] = None) -> Tuple[int, str]:
    args.insert(0, find_kubectl(["/bin", "/usr/bin", "/usr/local/bin", os.path.expanduser("~/bin")]))
    completed = run(args, shell=False, stdout=PIPE, stderr=STDOUT, env=env)

    return completed.returncode, completed.stdout
