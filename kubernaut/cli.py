import asyncio
import click
import logging
import typing

from kubernaut.kubernetes import read_kubeconfig, discover_cluster_id
from kubernaut.agent import *
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


CONTROLLER_HOST: str = "kubernaut.io"
CONTROLLER_PORT: int = 443
CONTROLLER_PROTO: str = "wss"


@click.command()
@click.option(
    "--controller-endpoint",
    envvar="KUBERNAUT_CONTROLLER_ENDPOINT",
    help="Configure remote Kubernaut Controller endpoint",
    default="wss://kubernaut.io/ws/capv1",
    type=str
)
@click.argument(
    "kubeconfig_file",
    envvar="KUBERNAUT_CLUSTER_KUBECONFIG_FILE",
    type=click.Path(exists=True)
)
@click.argument(
    "node_id",
    envvar="KUBERNAUT_NODE_ID",
    type=str
)
@click.argument(
    "join_token",
    envvar="KUBERNAUT_JOIN_TOKEN",
    type=str
)
def start_agent(controller_endpoint: str, kubeconfig_file: str, node_id: str, join_token: str):
    logger.info("Agent is starting...")

    agent_data = ensure_data_dir_exists(Path(click.get_app_dir("kubernaut-agent", force_posix=True)))
    agent_id = get_or_create_agent_id(agent_data)

    kubeconfig = read_kubeconfig(Path(kubeconfig_file))
    cluster_id = discover_cluster_id(namespace="default", kubeconfig=Path(kubeconfig_file))

    logger.info("Controller = %s", controller_endpoint)
    logger.info("Agent   ID = %s", agent_id)
    logger.info("Node    ID = %s", node_id)
    logger.info("Cluster ID = %s", cluster_id)
    logger.info("Join Token = %s", join_token)

    controller_endpoint += controller_endpoint + "?agent-id={}".format(str(agent_id))
    parsed_controller_endpoint = urlparse(controller_endpoint)

    cluster = ClusterDetail(cluster_id, kubeconfig, nodes={node_id}, state="UNREGISTERED", token=join_token)
    clusters = load_agent_state(agent_data / "clusters.json")
    if len(clusters) > 0:
        if cluster.id in clusters:
            logger.info("Agent found cluster in state file already")
    else:
        clusters[cluster.id] = cluster

    factory = create_agent_protocol_factory(controller_endpoint, agent_id, agent_data, clusters)

    loop = asyncio.get_event_loop()
    conn = loop.create_connection(factory, parsed_controller_endpoint.hostname, parsed_controller_endpoint.port)
    loop.run_until_complete(conn)
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    start_agent()
