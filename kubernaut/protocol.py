import json
import logging
import sys

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from json import JSONDecodeError

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CapV1Protocol(WebSocketClientProtocol):

    def __init__(self, factory, agent_id, cluster_id, kubeconfig):
        super().__init__()

        self.factory = factory
        self.agent_id = agent_id
        self.cluster_id = cluster_id
        self.kubeconfig = kubeconfig
        self.state = "disconnected"

    def __jsonify(self, obj):
        return json.dumps(obj)

    def _sendMessage(self, payload: str):
        self.sendMessage(payload.encode("UTF-8"), isBinary=False)

    def onConnect(self, response):
        logger.info("Agent connected to controller")

    def onOpen(self):
        logger.info("Agent CAPv1 session started")
        self.state = "connected"
        self._run()

    def onClose(self, wasClean, code, reason):
        logger.info("Agent CAPv1 session closed 'code = %s' 'reason = %s'", code, reason)
        self.state = "disconnected"

    def onMessage(self, payload, isBinary):
        self._process_message(payload)

    def _process_message(self, raw):
        try:
            msg = json.loads(raw)
        except JSONDecodeError as ex:
            print(ex)
            return

        msg_type = msg["@type"]
        if msg_type == "agent-sync-response":
            cluster_info = msg["clusters"].get(self.cluster_id, None)
            if cluster_info is not None:
                if cluster_info["status"] == "CLAIMED":
                    self.state = "claimed"
                elif cluster_info["status"] == "UNCLAIMED":
                    self.state = "registered"
                elif cluster_info["status"] == "DISCARDED":
                    self.state = "released"
        elif msg_type == "cluster-registration-response":
            cluster_info = msg["clusters"].get(self.cluster_id, None)
            if cluster_info and cluster_info["status"] == "ACCEPTED":
                self.state = "registered"
        elif msg_type == "cluster-claimed":
            self.state = "claimed"
        elif msg_type == "cluster-released":
            self.state = "released"

    def _run(self):
        state = self.state
        msg = None
        next_state = None

        if state == "connected":
            msg = {"@type": "agent-sync-request", "agentId": self.agent_id}
            next_state = "agent-sync-request:sent"

        elif state == "unregistered":
            msg = {
                "@type": "cluster-registration-request",
                "agentId": self.agent_id,
                "clusters": {self.cluster_id: {"kubeconfig": self.kubeconfig}}
            }
            next_state = "registering"

        elif state == "registered":
            msg = {
                "@type": "cluster-heartbeat",
                "agentId": self.agent_id,
                "clusters": [self.cluster_id]
            }

        if msg:
            self._sendMessage(self.__jsonify(msg))

        self.state = next_state
        self.factory.loop.call_later(1, self._run)
