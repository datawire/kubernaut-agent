import pytest

from kubernaut.model import Cluster


def test_cluster_shutdown():

    call_invocations = []

    def fake_handler(*args, **kwargs):
        call_invocations.append((args, kwargs))
        return 0, ""

    cluster = Cluster(
        cluster_id="FAKE_CLUSTER_ID", state="discarded", kubeconfig="FAKE_KUBECONFIG_DATA", token="FAKE_TOKEN"
    )

    cluster.shutdown(
        kubectl_handler=fake_handler,
        kubeadm_handler=fake_handler,
        system_handler=fake_handler
    )

    get_nodes_call = call_invocations[0]
    assert get_nodes_call[0][0] == ["get", "nodes", "--output=jsonpath={.items[*].metadata.name}"]
    assert get_nodes_call[0][1]["KUBECONFIG"] is not None

    assert call_invocations[-1 - 1] == ((["reset"],), {})
    assert call_invocations[-1] == (("systemctl poweroff",), {})
