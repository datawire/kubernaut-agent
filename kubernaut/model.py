import tempfile


class Cluster:

    def __init__(self, cluster_id: str, state: str, kubeconfig: str, token: str):
        self.cluster_id = cluster_id
        self.state = state
        self.kubeconfig = kubeconfig
        self.token = token

    def shutdown(self, kubectl_handler, kubeadm_handler, system_handler):
        with tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8", prefix="kubeconfig-") as fp:
            fp.write(self.kubeconfig)
            env_kubectl = {"KUBECONFIG": fp.name}

            (status, output) = kubectl_handler(
                ["get", "nodes", "--output=jsonpath={.items[*].metadata.name}"], env_kubectl)

            nodes = []
            if status == 0 and len(output) > 0:
                nodes = output.split(" ")

            for name in nodes:
                kubectl_handler(["drain", name, "--delete-local-data", "--force", "--ignore-daemonsets"], env_kubectl)
                kubectl_handler(["delete", "node", name], env_kubectl)

            # If we move to a world where there are multiple Kubernetes clusters handled by a single agent then this
            # code will need to be modified as the agent will not be installed per cluster most likely.
            kubeadm_handler(["reset"])
            system_handler("systemctl poweroff")
