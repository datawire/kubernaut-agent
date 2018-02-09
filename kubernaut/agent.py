import asyncio
import click
import logging
import sys
import typing

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from kubernaut.kubernetes import read_kubeconfig, discover_cluster_id
from kubernaut.protocol import CapV1Protocol

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
    logger.info("Started Kubernaut Agent")

    cluster_id = discover_cluster_id(namespace="default", kubeconfig=kubeconfig_file)
    kubeconfig = read_kubeconfig(kubeconfig_file)

    factory = WebSocketClientFactory(controller_endpoint)
    factory.protocol = CapV1Protocol
    factory.protocol.cluster_id = cluster_id
    factory.protocol.kubeconfig = kubeconfig

    loop = asyncio.get_event_loop()
    conn = loop.create_connection(factory, "127.0.0.1", 7000)
    loop.run_until_complete(conn)
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    agent()
