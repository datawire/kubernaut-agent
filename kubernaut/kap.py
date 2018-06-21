import logging

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from json import JSONDecodeError
from kubernaut.util import *
from kubernaut.model import Cluster
from typing import Any, Dict, List, Set
from uuid import UUID, uuid4


logger = logging.getLogger(__name__)


class Agent(WebSocketClientProtocol):

    def __init__(self, factory: WebSocketClientFactory, agent_id: UUID, clusters: Dict[str, Cluster]):
        super().__init__()
        self.factory = require(factory)

        self.agent_id = require(agent_id)
        self.agent_state = "unconnected"
        self.clusters = clusters

    def _set_agent_state(self, new_state):
        if new_state != self.current_state:
            old_state = self.current_state
            self.agent_state = new_state
            logger.info("agent state changed: '%s' -> '%s'", old_state, new_state)

    def _sendMessage(self, payload: str):
        self.sendMessage(payload.encode("utf-8"), isBinary=False)

    def _cluster_dict(self, cluster: Cluster):
        return {
            "id": cluster.cluster_id,
            "kubeconfig": cluster.kubeconfig,
            "state": cluster.state,
            "token": cluster.token
        }

    def onOpen(self):
        logger.info("CAPv1 session opened")
        self._set_agent_state("connected")
        self.run()

    def onClose(self, wasClean, code, reason):
        logger.info("CAPv1 session closed 'code = %s' 'reason = %s', 'clean = %s'", code, reason, wasClean)
        self._set_agent_state("disconnected")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                msg = unjsonify(payload)
                if not isinstance(msg, dict):
                    logger.warning("Received invalid payload")
                    return
                self._process_message(msg.get("@type", "unknown").lower(), msg)
            except JSONDecodeError:
                logger.exception("Received invalid JSON payload")
        else:
            logger.warning("Received binary payload that the agent cannot process")

    def run(self):
        if self.agent_state in ["disconnected", "unconnected"]:
            return  # connection retry logic

        clusters_to_send = {k: self._cluster_dict(v) for k, v in self.clusters}
        self._sendMessage(jsonify(clusters_to_send))

