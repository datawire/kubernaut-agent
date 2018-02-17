import pytest

from kubernaut.agent import *
from pathlib import Path
from uuid import UUID, uuid4


def test_ensure_data_dir_exists(tmpdir):
    dir_under_test = Path(tmpdir) / "kubernaut-agent"
    assert not dir_under_test.exists()

    data_dir = ensure_data_dir_exists(dir_under_test)

    assert isinstance(data_dir, Path)
    assert data_dir == dir_under_test
    assert data_dir.exists()


def test_get_or_create_agent_id_with_nonexistent_id_file(tmpdir):
    p = Path(tmpdir)
    id_file = p / "id"

    assert not id_file.is_file()
    assert not id_file.exists()
    created_id = get_or_create_agent_id(data_dir=p)

    assert isinstance(created_id, UUID)
    assert id_file.is_file()
    assert str(created_id) == id_file.read_text(encoding="UTF-8")


def test_get_or_create_agent_id_with_preexisting_id_file(tmpdir):
    p = Path(tmpdir)
    id_file = p / "id"

    identity = uuid4()
    id_file.write_text(str(identity), encoding="UTF-8")

    retrieved_id = get_or_create_agent_id(data_dir=p)
    assert identity == retrieved_id


def test_create_agent_protocol_factory(tmpdir):
    endpoint = "ws://localhost:7000/ws/capv1"
    agent_id = uuid4()

    cluster = ClusterDetail(cluster_id=str(uuid4()), kubeconfig="IAmTheWalrus", nodes={"i-test"}, state="UNCLAIMED")
    clusters = {cluster.id: cluster}

    factory = create_agent_protocol_factory(endpoint, agent_id, Path(tmpdir), clusters)
    agent = factory.protocol()

    assert isinstance(agent, Agent)
    assert agent.id == agent_id
    assert agent.data_dir == Path(tmpdir)
    assert agent.clusters == clusters


def test_load_nonexistent_agent_state(tmpdir):
    previous = load_agent_state(Path(tmpdir / "clusters.json"))
    assert previous == {}


def test_load_invalid_agent_state(tmpdir):
    p = Path(tmpdir) / "cluster.json"
    p.write_text("INVALID JSON")
    with pytest.raises(JSONDecodeError):
        load_agent_state(p)


def test_load_valid_agent_state(tmpdir):
    p = Path(tmpdir) / "cluster.json"
    p.write_text("""
{
    "6ec624c5-6742-40ce-b519-afc1c41c1444": {
        "kubeconfig": "__KUBECONFIG_DATA__", 
        "nodes": ["i-test-0"], 
        "state": "UNCLAIMED"
    },
    "9e606833-cd34-4df6-882a-c9b99409282d": {
        "kubeconfig": "__KUBECONFIG_DATA__", 
        "nodes": ["i-test-1", "i-test-2"], 
        "state": "CLAIMED"
    }
}
""")

    loaded = load_agent_state(p)
    assert len(loaded) == 2
    assert "6ec624c5-6742-40ce-b519-afc1c41c1444" in loaded
    assert "9e606833-cd34-4df6-882a-c9b99409282d" in loaded

    cl0 = ClusterDetail(cluster_id="6ec624c5-6742-40ce-b519-afc1c41c1444",
                        kubeconfig="__KUBECONFIG_DATA__",
                        state="UNCLAIMED",
                        nodes={"i-test-0"})

    assert loaded["6ec624c5-6742-40ce-b519-afc1c41c1444"] == cl0

    cl1 = ClusterDetail(cluster_id="9e606833-cd34-4df6-882a-c9b99409282d",
                        kubeconfig="__KUBECONFIG_DATA__",
                        state="CLAIMED",
                        nodes={"i-test-1", "i-test-2"})
    assert loaded["9e606833-cd34-4df6-882a-c9b99409282d"] == cl1
