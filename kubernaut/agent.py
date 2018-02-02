import asyncio
import click

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory


@click.command()
@click.option(
    "--controller-host",
    envvar="KUBERNAUT_CONTROLLER_HOST",
    help="Configure remote Kubernaut Controller host (fmt: host:port)",
    type=str
)
def agent(controller_host):
    print("Starting Kubernaut Agent...")
    start_agent()


class AgentProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        def hello():
            self.sendMessage(u"Hello, world!".encode('utf8'))
            self.factory.loop.call_later(1, hello)

        hello()

    def onMessage(self, payload, is_binary):
        if is_binary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, was_clean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


def start_agent():
    factory = WebSocketClientFactory("ws://127.0.0.1:7000")
    factory.protocol = AgentProtocol

    loop = asyncio.get_event_loop()
    conn = loop.create_connection(factory, "127.0.0.1", 7000)
    loop.run_until_complete(conn)
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    agent()
