import json
import logging
import typing
import sys

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from enum import Enum, unique
from json import JSONDecodeError

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@unique
class AgentState(Enum):
    UNREGISTERED = 1
    REGISTERED = 2
    CLAIMED = 3
    RELEASED = 4


class CapV1Protocol(WebSocketClientProtocol):

    cluster_id = None
    kubeconfig = None

    def __init__(self):
        super().__init__()
        self.state = AgentState.UNREGISTERED

    def onConnect(self, response):
        logger.info("Connected to Kubernaut Controller 'peer = %s'", response.peer)

    def onOpen(self):
        logger.info("CAPv1 session opened")
        self._run()

    def onClose(self, wasClean, code, reason):
        logger.info("CAPv1 session closed 'code = %s' 'reason = %s'", code, reason)
        self.state = AgentState.UNREGISTERED

    def _onMessage(self, payload, isBinary):
        logger.info("CAPv1 message received")
        self._process_message(payload)

    def _process_message(self, raw):
        try:
            msg = json.loads(raw)
        except JSONDecodeError as ex:
            print(ex)
            return

        msg_type = msg["@type"]
        if msg_type == "ClusterRegistrationResponse":
            if msg["status"] == "ACCEPTED":
                self.state = AgentState.REGISTERED
            else:
                logger.warning("Cluster 'id = %s'not registered 'status = %s'", CapV1Protocol.cluster_id, msg["status"])
        elif msg_type == "ClusterClaimed":
            self.state = AgentState.CLAIMED
        elif msg_type == "ClusterReleased":
            self.state = AgentState.RELEASED

    def __handle_cluster_registration_response(self, msg):
        if msg["status"] == "registered":
            self.state = AgentState.REGISTERED

            # configure heartbeat routine

    def _run(self):
        if self.state == AgentState.UNREGISTERED:
            logger.info("Sending cluster 'id = %s' registration", CapV1Protocol.cluster_id)
            msg = {
                "type": "ClusterRegistrationRequest",
                "clusterId": self.cluster_id,
                "kubeconfig": self.kubeconfig
            }
            print(json.dumps(msg))
            self.sendMessage(json.dumps(msg), isBinary=False)
        elif self.state == AgentState.REGISTERED:
            logger.info("Sending cluster 'id = %s' heartbeat", CapV1Protocol.cluster_id)
            msg = {
                "type": "ClusterRegistrationRequest",
                "clusterId": self.cluster_id,
            }
            self.sendMessage(json.dumps(msg), isBinary=False)

        self.factory.loop.call_later(1, self._run)
