import json
import logging
import typing
import sys

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from json import JSONDecodeError
from kubernaut.util import *
from kubernaut.node import shutdown
from pathlib import Path
from typing import Any, Dict, List, Set
from uuid import UUID, uuid4

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClusterDetail:

    def __init__(self, cluster_id: str, kubeconfig: str, state: str, token: str, nodes: Set[str]):
        self.id = require(cluster_id)
        self.kubeconfig = require_not_empty(kubeconfig)
        self.nodes = require_not_empty(nodes)
        self.state = require_not_empty(state)
        self.token = require_not_empty(token)

    def __str__(self): return str(self.__dict__)

    def __eq__(self, other): return self.__dict__ == other.__dict__


class Agent(WebSocketClientProtocol):

    def __init__(self, factory: WebSocketClientFactory, identity: UUID, data_dir: Path,
                 clusters: Dict[str, ClusterDetail]):

        super().__init__()
        self.factory = require(factory, "factory cannot be None")
        self.data_dir = require(data_dir, "data_dir cannot be None")
        self.id = require(identity, "identity cannot be None")
        self.clusters = require_not_empty(clusters, "clusters cannot be empty")
        self.state = "not_started"
        self.orphaned = []
        self.run_handle = None

    def _send_message(self, payload: str):
        self.sendMessage(payload.encode("UTF-8"), isBinary=False)

    def _create_agent_sync_request(self, cluster_ids: Set[str]) -> str:
        msg = {
            "@type": "cluster-heartbeat",
            "clusters": require_not_empty(cluster_ids)
        }
        return jsonify(msg)

    def _create_cluster_heartbeat(self, cluster_ids: Set[str]) -> str:
        msg = {
            "@type": "cluster-heartbeat",
            "clusters": require_not_empty(cluster_ids)
        }
        return jsonify(msg)

    def _create_cluster_registration_request(self, clusters: Dict[str, ClusterDetail]) -> str:
        msg = {
            "@type": "cluster-registration-request",
            "clusters": require_not_empty(clusters)
        }
        return jsonify(msg)

    def _process_message(self, msg_type: str, msg: Dict[str, Any]):
        if msg_type == "agent-sync-response":
            if self.state == "connected:syncing":
                self._handle_agent_sync_response(msg)
                self.state = "running"
            else:
                logger.warning("Received 'msg-type = %s' prematurely 'state = %s", msg_type, self.state)
                return
        elif msg_type == "cluster-registration-response":
            if self.state == "running":
                self._handle_cluster_registration_response(msg)
            else:
                logger.warning("Received 'msg-type = %s' prematurely 'state = %s", msg_type, self.state)
        elif msg_type in {"cluster-claimed", "cluster-discarded"}:
            pass

    def _handle_cluster_claimed(self, msg: Dict[str, Any]):
        cluster_id = msg["clusterId"]

        if cluster_id in self.clusters:
            self.clusters[cluster_id].state = "CLAIMED"
            write_agent_state(self.clusters, self.data_dir / "clusters.json")
        else:
            logger.warning("Agent notified about state of unknown cluster 'cluster = %s'", cluster_id)

    def _handle_cluster_released(self, msg: Dict[str, Any]):
        cluster_id = msg["clusterId"]

        if cluster_id in self.clusters:
            self.clusters[cluster_id].state = "DISCARDED"
            write_agent_state(self.clusters, self.data_dir / "clusters.json")
            shutdown()
        else:
            logger.warning("Agent notified about state of unknown cluster 'cluster = %s'", cluster_id)

    def _handle_agent_sync_response(self, response: Dict[str, Any]):
        synced_clusters = response.get("clusters", {})

        for cluster_id, status in synced_clusters.items():
            if cluster_id in self.clusters:
                claim_status = status["claimStatus"].upper()
                if claim_status in {"CLAIMED", "DISCARDED"}:
                    old_state = self.clusters[cluster_id].state
                    self.clusters[cluster_id].state = claim_status
                    logger.info("Agent notified of claim status change 'cluster = %s' 'transition = %s -> %s'",
                                cluster_id,
                                old_state,
                                claim_status)

                write_agent_state(self.clusters, self.data_dir / "clusters.json")
            else:
                logger.warning("Agent notified of orphaned cluster 'cluster = %s'", cluster_id)
                self.orphaned.append(cluster_id)

    def _handle_cluster_registration_response(self, response: Dict[str, Any]):
        registrants = response.get("clusters", {})

        for cluster_id, registration_detail in registrants.items():
            if cluster_id in self.clusters:
                r_status = registration_detail["status"].upper()
                if r_status == "ACCEPTED":
                    old_state = self.clusters[cluster_id].state
                    self.clusters[cluster_id].state = "REGISTERED"
                    logger.info("Agent notified of registration status change 'cluster = %s' 'transition = %s -> %s'",
                                cluster_id,
                                old_state,
                                r_status)

                write_agent_state(self.clusters, self.data_dir / "clusters.json")
            else:
                logger.warning("Agent notified of unknown cluster 'cluster = %s'", cluster_id)

    def onOpen(self):
        logger.info("CAPv1 session opened")
        self.state = "connected"
        self.run()

    def onClose(self, wasClean, code, reason):
        logger.info("CAPv1 session closed 'code = %s' 'reason = %s'", code, reason)
        self.state = "disconnected"

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
        if self.state == "connected":
            msg = self._create_agent_sync_request(cluster_ids=set(self.clusters.keys()))
            self.state = "connected:syncing"
            self._send_message(msg)

        if self.state == "running":
            heartbeats = set([])
            registrations = {}
            for cluster_id, cluster in self.clusters:
                if cluster.state == "UNCLAIMED":
                    heartbeats.add(cluster_id)
                elif cluster.state == "UNREGISTERED":
                    registrations[cluster_id] = cluster

            if len(heartbeats) > 0:
                msg = self._create_cluster_heartbeat(heartbeats)
                self._send_message(jsonify(msg))
            if len(registrations) > 0:
                msg = self._create_cluster_registration_request(registrations)
                self._send_message(jsonify(msg))

        self.run_handle = self.factory.loop.call_later(5, self.run)


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


def write_agent_state(state: Dict[str, ClusterDetail], state_file: Path):
    raw = {}
    for cluster_id, detail in state.items():
        raw[cluster_id] = {
            'id': detail.id,
            'state': detail.state,
            'token': detail.token,
            'nodes': list(detail.nodes),
            'kubeconfig': detail.kubeconfig
        }

    data = json.dumps(raw, indent=True)
    state_file.write_text(data, encoding="UTF-8")


def load_agent_state(state_file: Path) -> Dict[str, ClusterDetail]:
    try:
        raw = state_file.read_text(encoding="UTF-8")
        loaded = json.loads(raw, encoding="UTF-8")
        result = {}
        for k, v in loaded.items():
            result[k] = ClusterDetail(
                cluster_id=k,
                kubeconfig=v["kubeconfig"],
                token=v["token"],
                state=v["state"],
                nodes=set(v["nodes"])
            )

        return result
    except FileNotFoundError as fnf:
        return {}
