import asyncio
import click
import logging
import sys
import typing

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from kubernaut.kubernetes import read_kubeconfig, discover_cluster_id
from kubernaut.protocol import CapV1Protocol
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


CONTROLLER_HOST: str = "kubernaut.io"
CONTROLLER_PORT: int = 443
CONTROLLER_PROTO = "wss"


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
def agent(controller_endpoint: str, kubeconfig_file: str):
    logger.info("Agent is starting...")

    cs = ensure_configstore()
    logger.info("Agent config store 'path = %s'", cs)
    agent_id = ensure_agent_id(cs)
    logger.info("Agent identity 'id = %s'", agent_id)

    controller_endpoint += "?agent-id={}".format(agent_id)
    parsed_controller_url = urlparse(controller_endpoint)

    cluster_id = discover_cluster_id(namespace="default", kubeconfig=kubeconfig_file)
    kubeconfig = read_kubeconfig(kubeconfig_file)

    logger.info("Agent has started!")

    factory = WebSocketClientFactory(controller_endpoint)
    factory.protocol = lambda: CapV1Protocol(factory, agent_id, cluster_id, kubeconfig)

    loop = asyncio.get_event_loop()
    conn = loop.create_connection(factory, parsed_controller_url.hostname, parsed_controller_url.port)
    loop.run_until_complete(conn)
    loop.run_forever()
    loop.close()


def ensure_configstore() -> Path:
    cs = Path.home() / ".config" / "kubernaut-agent"
    cs.mkdir(parents=True, exist_ok=True)

    return cs


def ensure_agent_id(cs: Path) -> str:
    agent_id_file = cs / "id"
    agent_id_file.touch(exist_ok=True)

    agent_id = agent_id_file.read_text()
    if not agent_id:
        agent_id_file.write_text(str(uuid4()))

    return agent_id_file.read_text()


def ensure_cluster_store(cs: Path) -> Path:
    cluster_store = cs / "clusters.json"
    cluster_store.touch(exist_ok=True)

    return cluster_store


if __name__ == "__main__":
    agent()
