import asyncio
import click
import logging
import os
import sys
import time
import websockets

from kubernaut.model import Cluster
from kubernaut.util import *
from pathlib import Path
from subprocess import run, STDOUT, PIPE
from time import sleep
from typing import Dict, List, Mapping, Tuple
from uuid import UUID, uuid4

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_PATHS = ["/bin", "/usr/bin", "/usr/local/bin", os.path.expanduser("~/bin")]

cluster: Cluster = None

agent_id = None
agent_state: str = "starting"


@click.command()
@click.option(
    "--controller",
    envvar="KUBERNAUT_CONTROLLER_ADDRESS",
    help="Configure remote Kubernaut Controller address",
    default="wss://kubernaut.io/ws/capv1",
    type=str
)
@click.argument(
    "kubeconfig",
    envvar="KUBERNAUT_CLUSTER_KUBECONFIG",
    type=click.Path(exists=True)
)
@click.argument(
    "token",
    envvar="KUBERNAUT_TOKEN",
    type=str
)
def run_agent(controller: str, kubeconfig_file: str, token: str):
    logging.info("Agent is starting")
    logging.info("Agent is connecting to %s", controller)

    global agent_id, cluster

    agent_data = ensure_data_dir_exists(Path(click.get_app_dir("kubernaut-agent", force_posix=True)))
    agent_id = get_agent_id(agent_data)

    kubeconfig = read_kubeconfig(Path(kubeconfig_file))
    cluster_id = discover_cluster_id(namespace="default", kubeconfig=Path(kubeconfig_file))

    cluster = Cluster(
        cluster_id=cluster_id,
        state="UNREGISTERED",
        kubeconfig=kubeconfig,
        token=token
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run_agent(controller))


async def _run_agent(controller: str):
    global agent_id, agent_state, cluster
    controller = "{}?agent-id={}".format(controller, agent_id)
    async with websockets.connect(controller) as websocket:
        agent_state = "connected"
        while True:

            cluster_json = jsonify({
                "@type": "clusters-snapshot",
                "clusters": {
                    cluster.cluster_id: {
                        "id": cluster.cluster_id,
                        "token": cluster.token,
                        "detail": {"kubeconfig": cluster.kubeconfig},
                        "status": cluster.state
                    }
                }
            })

            await websocket.send(cluster_json)
            response = await websocket.recv()

            json_dict = unjsonify(response)
            if json_dict["@type"] == "clusters-snapshot":
                cluster.state = json_dict["clusters"][cluster.cluster_id]["status"]
            else:
                logger.warn("")

            sleep(2)


def ensure_data_dir_exists(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_agent_id(data_dir: Path) -> UUID:
    id_file = data_dir / "id"
    id_file.touch(exist_ok=True)

    identity = id_file.read_text()
    if not identity:
        identity = uuid4()
        id_file.write_text(str(identity), encoding="UTF-8")

    return UUID(identity) if isinstance(identity, str) else identity


def read_kubeconfig(kubeconfig_file: Path) -> str:
    return kubeconfig_file.read_text(encoding="UTF-8")


def discover_cluster_id(namespace: str = "default", kubeconfig: Path = (Path.home() / ".kube" / "config")) -> str:

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


def which(program: str, search: List[str] = None) -> str:
    for p in search:
        p = Path(p)
        p = p / program
        if p.is_file() and os.access(str(p), os.X_OK):
            return str(p)

    raise ValueError("Could not find `{}` program on system".format(program))


def kubectl(args: List[str], env: Mapping[str, str] = None) -> Tuple[int, str]:
    args.insert(0, which("kubectl", BIN_PATHS))
    completed = run(args, shell=False, stdout=PIPE, stderr=STDOUT, env=env)

    return completed.returncode, completed.stdout.decode("utf-8")


def kubeadm(args: List[str], env: Mapping[str, str] = None) -> Tuple[int, str]:
    args.insert(0, which("kubeadm", BIN_PATHS))
    completed = run(args, shell=False, stdout=PIPE, stderr=STDOUT, env=env)

    return completed.returncode, completed.stdout.decode("utf-8")


if __name__ == "__main__":
    run_agent()
