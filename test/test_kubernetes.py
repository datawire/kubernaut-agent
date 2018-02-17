import pytest

from kubernaut.kubernetes import *
from pathlib import Path


def test_read_kubeconfig_existent_kubeconfig(tmpdir):
    kubeconfig_file = Path(tmpdir) / ".kube" / "config"
    kubeconfig_file.parent.mkdir(exist_ok=True)

    kubeconfig_data = """
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: REDACTED
    server: https://52.90.0.114:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: admin
  name: admin@kubernetes
current-context: admin@kubernetes
kind: Config
preferences: {}
users:
- name: admin
  user:
    client-certificate-data: REDACTED
    client-key-data: REDACTED
"""

    kubeconfig_file.write_text(kubeconfig_data)

    read_kubeconfig_data = read_kubeconfig(kubeconfig_file)
    assert read_kubeconfig_data == kubeconfig_data


def test_read_kubeconfig_nonexistent_kubeconfig(tmpdir):
    kubeconfig_file = Path(tmpdir) / ".kube" / "config"
    with pytest.raises(FileNotFoundError):
        read_kubeconfig(kubeconfig_file)
