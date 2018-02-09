import asyncio
import click
import json
import logging
import sys

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from kubernaut.kubernetes import read_kubeconfig, discover_cluster_id
from kubernaut.protocol import CapV1Protocol

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


CONTROLLER_HOST = "kubernaut.io"
CONTROLLER_PORT = 443
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
def agent(controller_endpoint, kubeconfig_file):
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


class AgentProtocol(WebSocketClientProtocol):

    def __init__(self, tenant_id, pool_name, kubeconfig_file):
        super().__init__()
        self.state = "unregistered"

        self.tenant_id = tenant_id
        self.pool_name = pool_name
        self.kubeconfig_file = kubeconfig_file
        self.cluster_id = None

    def onConnect(self, response):
        print("Connected to remote 'address = {0}'".format(response.peer))

    def onOpen(self):
        self._register()

    def onMessage(self, payload, is_binary):
        data = json.loads(payload, encoding="utf-8")
        self._handle_received_message(data)

    def onClose(self, was_clean, code, reason):
        self.state = "unregistered"

    def _register(self):
        if not self.state == "claimed":
            msg = {
                "type": "registration",
                "cluster": {
                    "poolName": self.pool_name,
                    "kubeconfig": self.kubeconfig_file
                }
            }

            self.sendMessage(json.dumps(msg))

        self.factory.loop.call_later(1, self._register)

    def _handle_registration_accepted(self):
        self.state = "registration:accepted"

    def _handle_claim(self):
        self.state = "claimed"

    def _handle_received_message(self, msg):
        msg_types = {
            "registration:accepted": self._handle_registration_accepted,
            "claimed": self._handle_claim
        }

        try:
            msg_types[msg["type"].tolower()](msg)
        except KeyError:
            pass


def load_kubeconfig(kubeconfig_path):
    from pathlib import Path
    return Path(kubeconfig_path).read_text(encoding="utf-8")


if __name__ == "__main__":
    agent()
