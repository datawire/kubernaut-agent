import asyncio
import click
import logging
import sys
import websockets

from kubernaut.model import Cluster
from kubernaut.kubernetes import *
from kubernaut.util import *
from pathlib import Path
from time import sleep
from uuid import UUID, uuid4

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("agent")

cluster: Cluster = None

agent_id = None
agent_state: str = "starting"


@click.command()
@click.option(
    "--controller",
    envvar="KUBERNAUT_CONTROLLER_ADDRESS",
    help="Configure remote Kubernaut Controller address",
    default="wss://next.kubernaut.io/beta/ws/kapv1",
    type=str
)
@click.option(
    "--cluster-shutdown",
    envvar="KUBERNAUT_CLUSTER_SHUTDOWN",
    default=True,
    type=bool
)
@click.argument(
    "kubeconfig_file",
    envvar="KUBERNAUT_CLUSTER_KUBECONFIG",
    type=click.Path(exists=True)
)
@click.argument(
    "token",
    envvar="KUBERNAUT_CLUSTER_GROUP_TOKEN",
    type=str
)
def run_agent(controller: str, cluster_shutdown: bool, kubeconfig_file: str, token: str):
    logging.info("Agent is %s", agent_state)
    logging.info("Agent is connecting to %s", controller)
    logging.info("Agent cluster shutdown %s", ("enabled" if cluster_shutdown else "disabled"))

    global agent_id, cluster

    agent_data = ensure_data_dir_exists(Path(click.get_app_dir("kubernaut-agent", force_posix=True)))
    agent_id = get_agent_id(agent_data)

    logging.info("Agent ID is: %s", agent_id)

    kubeconfig = read_kubeconfig(Path(kubeconfig_file))
    cluster_id = discover_cluster_id(namespace="default", kubeconfig=Path(kubeconfig_file))

    logging.info("Cluster ID is: %s", cluster_id)

    cluster = Cluster(
        cluster_id=cluster_id,
        state="UNREGISTERED",
        kubeconfig=kubeconfig,
        token=token
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run_agent(controller, cluster_shutdown))


async def _run_agent(controller: str, cluster_shutdown: bool):
    global agent_id, agent_state, cluster
    controller_url = "{}?agent-id={}".format(controller, str(agent_id))
    async with websockets.connect(controller_url) as websocket:
        agent_state = "connected"
        logging.info("Agent is %s", agent_state)
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
            }, indent=True)

            await websocket.send(cluster_json)
            logger.info("Cluster snapshot sent,     cluster: %s, state: %s", cluster.cluster_id, cluster.state)
            response = await websocket.recv()

            json_dict = unjsonify(response)
            if json_dict["@type"] == "clusters-snapshot":
                status = json_dict["clusters"][cluster.cluster_id]["status"]
                logger.info("Cluster snapshot received, cluster: %s, state: %s", cluster.cluster_id, status)
                cluster.state = status
            else:
                logger.warning("Received unknown message type: %s", json_dict["@type"])

            if cluster.state.lower() in ["discarded", "expired", "released"]:
                def do_nothing_handler(*args, **kwargs):
                    return 0, ""

                # this is some drop dead stupid code, but under local dev scenarios I would be very annoyed if localhost
                # did something like shutdown my cluster or my computer.
                if cluster_shutdown:
                    cluster.shutdown(
                        kubectl_handler=kubectl,
                        kubeadm_handler=kubeadm,
                        system_handler=os.system,
                    )
                else:
                    logging.info("Cluster shutdown disabled")
                    return

            sleep(5)


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


if __name__ == "__main__":
    run_agent()
