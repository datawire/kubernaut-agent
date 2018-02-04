import asyncio
import click
import json

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory


CONTROLLER_HOST = "kubernaut.io"
CONTROLLER_PORT = 443
CONTROLLER_PROTO = "wss"


@click.command()
@click.option(
    "--controller-endpoint",
    envvar="KUBERNAUT_CONTROLLER_ENDPOINT",
    help="Configure remote Kubernaut Controller endpoint",
    default="wss://kubernaut.io/cap-v1",
    type=str
)
@click.argument(
    "cluster_id",
    envvar="KUBERNAUT_CLUSTER_ID",
)
@click.argument(
    "kubeconfig_file",
    envvar="KUBERNAUT_CLUSTER_KUBECONFIG_FILE",
)
def agent(controller_endpoint, cluster_id, kubeconfig_file):
    print("Starting Kubernaut Agent...")
    factory = WebSocketClientFactory("ws://127.0.0.1:7000/cap-v1")
    factory.protocol = AgentProtocol

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
