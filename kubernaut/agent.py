import json
import logging
import typing
import sys

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from json import JSONDecodeError
from kubernaut.util import *
from pathlib import Path
from typing import Any, Dict, List, Set
from uuid import UUID, uuid4

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClusterDetail:

    def __init__(self, cluster_id: str, kubeconfig: str, state: str, nodes: Set[str]):
        self.id = require(cluster_id)
        self.kubeconfig = require_not_empty(kubeconfig)
        self.nodes = require_not_empty(nodes)
        self.state = require_not_empty(state)

    def __str__(self): return str(self.__dict__)

    def __eq__(self, other): return self.__dict__ == other.__dict__


class Agent(WebSocketClientProtocol):

    def __init__(self, factory: WebSocketClientFactory, identity: UUID, data_dir: Path, clusters: Dict[str, ClusterDetail]):
        super().__init__()
        self.factory = require(factory, "factory cannot be None")
        self.data_dir = require(data_dir, "data_dir cannot be None")
        self.id = require(identity, "identity cannot be None")
        self.clusters = require_not_empty(clusters, "clusters cannot be empty")
        self.state = "not_started"

    def _jsonify(self, obj: Any) -> str:
        return json.dumps(require(obj), indent=True)

    def _unjsonify(self, data: str) -> Dict[str, Any]:
        return json.loads(data)

    def _send_message(self, payload: str):
        self.sendMessage(payload.encode("UTF-8"), isBinary=False)

    def _create_agent_sync_request(self, cluster_ids: Set[str]) -> str:
        msg = {"@type": "cluster-heartbeat", "clusters": require_not_empty(cluster_ids)}
        return self._jsonify(msg)

    def _create_cluster_heartbeat(self, cluster_ids: Set[str]) -> str:
        msg = {"@type": "cluster-heartbeat", "clusters": require_not_empty(cluster_ids)}
        return self._jsonify(msg)

    def _create_cluster_registration_request(self, clusters: Dict[str, Any]) -> str:
        msg = {"@type": "cluster-registration-request", "clusters": require_not_empty(clusters)}
        return self._jsonify(msg)

    def _process_message(self, msg_type: str, msg: Dict[str, Any]):
        if msg_type == "agent-sync-response":
            pass
        elif msg_type == "cluster-registration-response":
            pass
        elif msg_type == "cluster-claimed":
            pass
        elif msg_type == "cluster-discarded":
            pass

    def onOpen(self):
        logger.info("CAPv1 session opened")
        self.state = "connected"
        self._run()

    def onClose(self, wasClean, code, reason):
        logger.info("CAPv1 session closed 'code = %s' 'reason = %s'", code, reason)
        self.state = "disconnected"

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                msg = json.loads(payload)
                if not isinstance(msg, dict):
                    logger.warning("Received invalid payload")
                    return
                self._process_message(msg.get("@type", "unknown").lower(), msg)
            except JSONDecodeError as ex:
                logger.error("Received invalid JSON payload", ex)
                return
        else:
            logger.warning("Received binary payload that the agent cannot process")


def ensure_data_dir_exists(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_or_create_agent_id(data_dir: Path) -> UUID:
    id_file = data_dir / "id"
    id_file.touch(exist_ok=True)

    identity = id_file.read_text()
    if not identity:
        identity = uuid4()
        id_file.write_text(str(identity), encoding="UTF-8")

    return UUID(identity) if isinstance(identity, str) else identity


def create_agent_protocol_factory(ctrl_endpoint: str,
                                  agent_id: UUID,
                                  agent_data: Path,
                                  clusters: Dict[str, ClusterDetail]) -> WebSocketClientFactory:

    factory = WebSocketClientFactory(ctrl_endpoint)
    factory.protocol = lambda: Agent(factory, agent_id, agent_data, clusters)

    return factory


def load_agent_state(state_file: Path) -> Dict[str, ClusterDetail]:
    try:
        raw = state_file.read_text(encoding="UTF-8")
        loaded = json.loads(raw, encoding="UTF-8")
        result = {}
        for k, v in loaded.items():
            result[k] = ClusterDetail(k, v["kubeconfig"], v["state"], set(v["nodes"]))

        return result
    except FileNotFoundError as fnf:
        return {}
